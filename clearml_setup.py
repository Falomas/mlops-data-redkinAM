"""Создание трёх версий ClearML Dataset для практики."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path

import pandas as pd
from clearml import Dataset
from sklearn.datasets import load_iris, load_wine


PROJECT = "MIIT/MLOps/practice_3/redkinAM"
NAME = "sklearn-tabular-redkinAM"


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    """Детерминированное сохранение CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = frame.sort_values(list(frame.columns), kind="mergesort").reset_index(drop=True)
    ordered.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def sha256_file(path: Path) -> str:
    """SHA-256 файла."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(path: Path) -> dict:
    """Краткая сводка по CSV."""
    frame = pd.read_csv(path)
    return {
        "file": path.name,
        "sha256": sha256_file(path),
        "rows": len(frame),
        "columns": list(frame.columns),
        "shape": frame.shape,
    }


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="clearml_redkinAM_"))
    base_dir = work / "base"
    wine_dir = work / "wine_only"
    features_dir = work / "features"
    for folder in (base_dir, wine_dir, features_dir):
        folder.mkdir()

    # Базовые таблицы
    iris = load_iris(as_frame=True).frame
    wine = load_wine(as_frame=True).frame
    iris_feat = iris.copy()
    iris_feat["sepal_area"] = iris_feat["sepal length (cm)"] * iris_feat["sepal width (cm)"]
    iris_feat["petal_area"] = iris_feat["petal length (cm)"] * iris_feat["petal width (cm)"]

    save_csv(iris, base_dir / "iris.csv")
    save_csv(wine, wine_dir / "wine.csv")
    save_csv(iris_feat, features_dir / "iris.csv")

    # 1.0.0 base
    base = Dataset.create(
        dataset_project=PROJECT,
        dataset_name=NAME,
        dataset_version="1.0.0",
        dataset_tags=["base"],
        description="Исходный Iris без дополнительных признаков",
    )
    base.add_files(path=str(base_dir / "iris.csv"))
    base.upload()
    base.finalize()
    base_id = base.id
    print("BASE_ID:", base_id)
    print("BASE files:", base.list_files())

    # 1.1.0 wine child
    wine_ds = Dataset.create(
        dataset_project=PROJECT,
        dataset_name=NAME,
        dataset_version="1.1.0",
        parent_datasets=[base_id],
        dataset_tags=["wine"],
        description="Добавлен Wine, Iris наследуется от базы",
    )
    wine_ds.add_files(path=str(wine_dir / "wine.csv"))
    wine_ds.upload()
    wine_ds.finalize()
    wine_id = wine_ds.id
    print("WINE_ID:", wine_id)
    print("WINE files:", wine_ds.list_files())
    print("WINE added:", wine_ds.list_added_files())
    print("WINE parents:", wine_ds.get_dependency_graph())

    # 2.0.0 iris features от базы
    feat_ds = Dataset.create(
        dataset_project=PROJECT,
        dataset_name=NAME,
        dataset_version="2.0.0",
        parent_datasets=[base_id],
        dataset_tags=["iris_features"],
        description="Iris с sepal_area и petal_area, без Wine",
    )
    feat_ds.add_files(path=str(features_dir / "iris.csv"))
    feat_ds.upload()
    feat_ds.finalize()
    feat_id = feat_ds.id
    print("IRIS_FEATURES_ID:", feat_id)
    print("FEATURES files:", feat_ds.list_files())
    print("FEATURES modified:", feat_ds.list_modified_files())
    print("FEATURES parents:", feat_ds.get_dependency_graph())

    # Скачивание в три разные папки
    downloads = work / "downloads"
    results = []
    for label, ds_id in [
        ("1.0.0", base_id),
        ("1.1.0", wine_id),
        ("2.0.0", feat_id),
    ]:
        target = downloads / label.replace(".", "_")
        target.mkdir(parents=True)
        ds = Dataset.get(dataset_id=ds_id)
        ds.get_mutable_local_copy(target_folder=str(target), overwrite=False)
        info = {
            "version": label,
            "id": ds_id,
            "parents": list(ds.get_dependency_graph().keys()) if ds.get_dependency_graph() else [],
            "dependency_graph": ds.get_dependency_graph(),
            "files": ds.list_files(),
            "added": ds.list_added_files(),
            "modified": ds.list_modified_files(),
            "removed": ds.list_removed_files(),
            "local": [],
        }
        for csv_path in sorted(target.rglob("*.csv")):
            info["local"].append(describe(csv_path))
        results.append(info)
        print("---")
        print(info)

    # Сохраняем краткий результат для отчёта
    out = Path("clearml_ids.txt")
    lines = [
        f"BASE_ID={base_id}",
        f"WINE_ID={wine_id}",
        f"IRIS_FEATURES_ID={feat_id}",
        f"PROJECT={PROJECT}",
        f"NAME={NAME}",
    ]
    for item in results:
        lines.append(str(item))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved", out)

    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
