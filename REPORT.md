# Отчёт: версионирование данных с DVC и ClearML

Студент: **redkinAM**  
Репозиторий: локальный `mlops-data-redkinAM`  
(путь: `C:\Users\Anton\Documents\VSCode\python\dz3\mlops-data-redkinAM`)

## Версии окружения

| Пакет | Версия |
|---|---|
| Python | 3.12.14 |
| DVC | 3.67.1 |
| ClearML | 2.1.12 |
| pandas | 3.0.6 |
| scikit-learn | 1.9.1 |

Зависимости также зафиксированы в `pyproject.toml` и `poetry.lock`.

## DVC remote

Локальный remote вне репозитория:

```text
C:\Users\Anton\Documents\VSCode\python\dz3\dvc-remote-redkinAM
```

Имя remote: `storage` (default). Секретов нет.

## Git commits и tags

| Метка / ветка | Commit | Описание |
|---|---|---|
| tag `data-v1` / база | `930e13a63c8b943993b3caab3f725298d1e668d8` | только `iris.csv` |
| `feature/wine` | `c6d0c33` | добавлен `wine.csv` |
| `feature/iris-features` | `90c464c` | Iris с `sepal_area`, `petal_area` |
| merge / `main` HEAD | `6c292fc40eb73a3f8ad1688c1ddd47d64f13595d` | итог: Iris+features и Wine |

## Хэши DVC

| Объект | SHA-256 / md5 |
|---|---|
| итоговый `data.dvc` | `96dfda4219f2457ea0fdce7cb7d69cb89dd0e55680d6be9b639f3f5624c1aefb` |
| md5 директории `data` (из `data.dvc`) | `957c42d7c9ecafed014287db892a5935.dir` |
| `iris.csv` (итоговый, с признаками) | `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26` |
| `wine.csv` | `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60` |
| `iris.csv` (база data-v1) | `6d700503c9c2e2c71d187b889a87af8a8d3a6dd5bae1266d46f4ee4db5a6349f` |

## Восстановление из чистого clone

1. `git clone` репозитория в новую директорию `mlops-data-redkinAM-clone`.
2. `dvc pull` из remote `storage`.
3. `python check_data.py` — проверка пройдена.

Получены те же SHA-256:

- iris.csv: `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26` (150×7)
- wine.csv: `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60` (178×14)

## ClearML Dataset

- Project: `MIIT/MLOps/practice_3/redkinAM`
- Name: `sklearn-tabular-redkinAM`

| Переменная | Dataset ID | Version | Parent | Состав |
|---|---|---|---|---|
| `BASE_ID` | `de17ca23c9e2411f911e42b9cfd79068` | 1.0.0 | — | только `iris.csv` |
| `WINE_ID` | `6cae7ef77c2f4ae6942c32f406d9ecdd` | 1.1.0 | `BASE_ID` | `iris.csv` + `wine.csv` |
| `IRIS_FEATURES_ID` | `0562cf0cb22a4d3483927cd1d7e170db` | 2.0.0 | `BASE_ID` | изменённый `iris.csv` |

### Dependency graph

```text
de17ca23... (1.0.0 base) ──┬── 6cae7ef7... (1.1.0 wine)
                           └── 0562cf0c... (2.0.0 iris_features)
```

Версии `1.1.0` и `2.0.0` — две ветви от одной базы. У `2.0.0` parent = `BASE_ID`, а не `WINE_ID`.

### Скачанные версии

**1.0.0** (`BASE_ID`)

- files: `iris.csv`
- added: `iris.csv`
- iris SHA-256: `6d700503c9c2e2c71d187b889a87af8a8d3a6dd5bae1266d46f4ee4db5a6349f`
- форма: 150×5, столбцы: sepal/petal length/width, target

**1.1.0** (`WINE_ID`)

- files: `iris.csv`, `wine.csv`
- added: `wine.csv`
- iris SHA-256: тот же, что у базы
- wine SHA-256: `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60`
- формы: 150×5 и 178×14

**2.0.0** (`IRIS_FEATURES_ID`)

- files: `iris.csv`
- modified: `iris.csv`
- iris SHA-256: `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26`
- форма: 150×7, добавлены `sepal_area`, `petal_area`
- `wine.csv` отсутствует

## Сравнительная таблица (наблюдения из работы)

| Свойство | DVC | ClearML Dataset |
|---|---|---|
| Идентификатор версии | Git commit + хэш в `data.dvc` (например `6c292fc` и md5 `957c42d7...`) | Dataset ID (`de17ca23...`, `6cae7ef7...`, `0562cf0c...`) |
| Расположение метаданных | `.dvc`-файлы и `.dvc/config` в Git | ClearML Server (project/name/version + ID) |
| Расположение файлов | DVC cache + remote `dvc-remote-redkinAM` | ClearML File Server `files.clear.ml` |
| Создание дочерней версии | Новая Git-ветка + `dvc add` + commit | `Dataset.create(..., parent_datasets=[BASE_ID])` |
| Переключение версии | `git switch` + `dvc checkout` | `Dataset.get(dataset_id=...)` |
| Восстановление на чистой машине | `git clone` + `dvc pull` — проверено на clone | `Dataset.get` + `get_mutable_local_copy` в пустую папку |
| Ветвление | Две Git-ветки `feature/wine` и `feature/iris-features` | Две ветви lineage от `BASE_ID` |
| Слияние | `git merge` + DVC merge driver объединил `data.dvc` автоматически | Несколько parents или новая производная версия; в этой работе слияние делали только в DVC |
| Связь с Git | Версия данных жёстко связана с коммитом | Dataset существует независимо от Git |
| UI | Нет встроенного UI (только локальные команды) | Web UI: app.clear.ml, страницы datasets |

## Ответы на вопросы

1. **Какой объект однозначно определяет версию данных в DVC?**  
   Пара: Git-коммит (состояние `data.dvc`) и содержимое в DVC cache/remote по md5 из `.dvc`-файла. Одного имени файла недостаточно.

2. **Почему одного Git-коммита недостаточно без DVC remote?**  
   В Git лежит только маленький `data.dvc`. Сами CSV в remote/cache. Без `dvc push`/`dvc pull` чистый clone получит метаданные, но не восстановит файлы.

3. **Чем Dataset version отличается от Dataset ID?**  
   Version (`1.0.0`) — человекочитаемая метка, её можно повторить или перепутать. Dataset ID — уникальный идентификатор конкретной финализированной версии.

4. **Почему `finalize()` нельзя считать созданием следующей версии?**  
   `finalize()` только закрывает текущую mutable-версию и делает её immutable. Следующую версию создаёт новый `Dataset.create(...)`.

5. **Как доказать, что version `2.0.0` создана от базы, а не от `1.1.0`?**  
   По `get_dependency_graph()`: parent у `0562cf0c...` равен `de17ca23...` (`BASE_ID`). `WINE_ID` в предках нет. В составе нет `wine.csv`, modified = `iris.csv`.

6. **Что будет, если после `git switch` не сделать `dvc checkout`?**  
   Обновится только `data.dvc`, а файлы в `data/` могут остаться от предыдущей ветки. Например, после перехода на `main` с базой `wine.csv` мог бы остаться в workspace.

7. **Когда удобнее DVC, а когда ClearML?**  
   DVC удобнее, когда данные должны жить вместе с Git-ветками и code review (как merge `feature/wine` и `feature/iris-features`). ClearML удобнее для отдельного lineage датасетов, UI и шаринга версий по Dataset ID без клонирования всего Git-репозитория.
