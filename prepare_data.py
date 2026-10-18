"""Генератор версий таблиц Iris и Wine."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris, load_wine


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    """Сохраняет таблицу детерминированно: сортировка и одинаковый формат CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = frame.sort_values(list(frame.columns), kind="mergesort").reset_index(drop=True)
    ordered.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def make_base(data_dir: Path) -> None:
    """Режим base: только исходный Iris."""
    iris = load_iris(as_frame=True).frame
    save_csv(iris, data_dir / "iris.csv")


def make_wine(data_dir: Path) -> None:
    """Режим wine: добавить Wine, Iris не трогать."""
    wine = load_wine(as_frame=True).frame
    save_csv(wine, data_dir / "wine.csv")


def make_iris_features(data_dir: Path) -> None:
    """Режим iris_features: добавить sepal_area и petal_area в Iris."""
    iris = load_iris(as_frame=True).frame
    iris["sepal_area"] = iris["sepal length (cm)"] * iris["sepal width (cm)"]
    iris["petal_area"] = iris["petal length (cm)"] * iris["petal width (cm)"]
    save_csv(iris, data_dir / "iris.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Подготовка версий данных")
    parser.add_argument(
        "mode",
        choices=["base", "wine", "iris_features"],
        help="Режим генерации данных",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Директория для CSV (по умолчанию data)",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    if args.mode == "base":
        make_base(data_dir)
    elif args.mode == "wine":
        make_wine(data_dir)
    else:
        make_iris_features(data_dir)

    print(f"Готово: режим {args.mode}, директория {data_dir}")


if __name__ == "__main__":
    main()
