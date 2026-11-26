# Troubleshooting

[Docs home](README.md) › Troubleshooting

Symptoms people hit when installing or using `base-tdb-models`, with the cause and the fix. If yours is not here, open an issue with the full error and the commit you are on.

| Symptom | Likely cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'talkingdb'` | The package is not installed in the active environment, or a service is run with system Python instead of its Poetry environment | Run `poetry install` in the consuming repository, then run through `poetry run`. For side by side development, use `make sync MODE=local` in that repository so it points at your local checkout |
| `ModuleNotFoundError: No module named 'smart_slugify'` | Dependencies were not installed, only the source folder was put on `PYTHONPATH` | Install the dependencies listed in [pyproject.toml](../pyproject.toml): `poetry install`, or `pip install smart-slugify networkx "pydantic[email]"` |
| Poetry refuses to install: Python version not supported | `requires-python` is `>=3.12,<3.14` | Use Python 3.12 or 3.13. Check with `python --version` |
| A consumer behaves differently from this repository's `main` | Consumers pin a commit, which can be older than `main` | Compare the `rev` in the consumer's `pyproject.toml` with `git log`. See [who depends on this](architecture.md#who-depends-on-this-and-at-which-commit) |
| A synonym lookup returns two or more entities | The same [surface text](https://github.com/TalkingDB/ConceptDigger/blob/master/docs/concepts.md#surface-texts-every-name-for-a-thing) was added to more than one entity | This is by design: `get_entities_by_surface_text` returns every claimant. Remove the duplicate with `update_surface_texts`, or let the caller choose |
| Entities saved earlier disappeared | `save(conn)` defaults to `overwrite=True`, which deletes every row for that `entity_id` before writing | Load, change, then save the whole graph. Pass `overwrite=False` only when you are appending rows that do not exist yet |
| `sqlite3.OperationalError: database is locked` | Two writers hold [SQLite](https://www.sqlite.org/about.html)'s single write lock at once | Open connections with [base-tdb-clients](https://github.com/TalkingDB/base-tdb-clients), which sets WAL mode and a 30 second busy timeout (`TDB_SQLITE_BUSY_TIMEOUT_MS`). For large graphs, lower `batch_size` in `GraphModel.save` |
| Old rows load with missing or wrong fields after an upgrade | A model's stored shape changed and the SQLite file was written by an older commit | Nothing migrates automatically. Rebuild the store, or write a one off migration, before bumping the pin |

## Before you open an issue

1. Note the commit: `git rev-parse --short HEAD`.
2. Note the Python version and the versions of `pydantic` and `networkx`.
3. Reduce the problem to a few lines like the examples in [usage-and-examples.md](usage-and-examples.md).

## Further reading

- [SQLite write ahead logging](https://www.sqlite.org/wal.html): why WAL mode lets readers and one writer work together
- [Poetry: managing environments](https://python-poetry.org/docs/managing-environments/): making sure the right Python runs your code

---

**Related:** [Architecture](architecture.md) · [Usage and examples](usage-and-examples.md) · [README](../README.md)
