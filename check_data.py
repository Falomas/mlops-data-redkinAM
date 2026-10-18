"""Проверка CSV: хэши, форма, столбцы и вычисляемые признаки."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris, load_wine


def sha256_file(path: Path) -> str:
    """Считает SHA-256 файла."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_iris(path: Path) -> None:
    """Проверяет iris.csv относительно исходного Dataset."""
    if not path.exists():
        raise SystemExit(f"Отсутствует ожидаемый файл: {path}")

    frame = pd.read_csv(path)
    expected_rows = len(load_iris(as_frame=True).frame)

    if "" in frame.columns or "Unnamed: 0" in frame.columns:
        raise SystemExit(f"В {path} найден безымянный столбец индекса")

    if len(frame) != expected_rows:
        raise SystemExit(
            f"{path}: строк {len(frame)}, ожидалось {expected_rows}"
        )

    required = [
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
        "target",
    ]
    for column in required:
        if column not in frame.columns:
            raise SystemExit(f"{path}: нет столбца {column}")

    # Если есть вычисляемые столбцы — проверяем значения
    if "sepal_area" in frame.columns:
        expected = frame["sepal length (cm)"] * frame["sepal width (cm)"]
        if not (frame["sepal_area"] - expected).abs().le(1e-9).all():
            raise SystemExit(f"{path}: неверные значения sepal_area")

    if "petal_area" in frame.columns:
        expected = frame["petal length (cm)"] * frame["petal width (cm)"]
        if not (frame["petal_area"] - expected).abs().le(1e-9).all():
            raise SystemExit(f"{path}: неверные значения petal_area")

    print_info(path, frame)


def check_wine(path: Path) -> None:
    """Проверяет wine.csv относительно исходного Dataset."""
    if not path.exists():
        raise SystemExit(f"Отсутствует ожидаемый файл: {path}")

    frame = pd.read_csv(path)
    expected_rows = len(load_wine(as_frame=True).frame)

    if "" in frame.columns or "Unnamed: 0" in frame.columns:
        raise SystemExit(f"В {path} найден безымянный столбец индекса")

    if len(frame) != expected_rows:
        raise SystemExit(
            f"{path}: строк {len(frame)}, ожидалось {expected_rows}"
        )

    print_info(path, frame)


def print_info(path: Path, frame: pd.DataFrame) -> None:
    """Печатает сводку по файлу."""
    print(f"path: {path.as_posix()}")
    print(f"sha256: {sha256_file(path)}")
    print(f"rows: {len(frame)}")
    print(f"columns: {len(frame.columns)}")
    print(f"column_list: {list(frame.columns)}")
    print(f"missing: {int(frame.isna().sum().sum())}")
    print("---")


def main() -> None:
    data_dir = Path("data")
    iris_path = data_dir / "iris.csv"
    wine_path = data_dir / "wine.csv"

    # Iris обязателен во всех итоговых сценариях этой работы
    check_iris(iris_path)

    if wine_path.exists():
        check_wine(wine_path)
    else:
        print(f"path: {wine_path.as_posix()}")
        print("status: отсутствует (это допустимо для части версий)")
        print("---")

    print("Проверка пройдена")


if __name__ == "__main__":
    main()
