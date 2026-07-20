# Development

Install the locked development environment and run the complete local checks:

```console
uv sync --all-groups
make lint
make test
make build
```

Use `make format` to apply Ruff formatting and safe lint fixes. `make clean`
removes caches and build artifacts. `make help` lists all targets.

CI checks formatting, linting, and strict mypy on Python 3.14. The test matrix
runs on Python 3.11, 3.12, 3.13, and 3.14 using `uv sync --all-groups --locked`.

## Releases

Set `[project].version` in `pyproject.toml`, finish the changelog, and create a
clean release tag with `make sys/tag`. Tags use `vX.Y.Z` (for example,
`v1.0.0`) and must match the project version. The publish workflow verifies the
tag, runs all quality checks and tests, builds distributions once, and publishes
them through PyPI trusted publishing. No PyPI password is stored in GitHub
Actions.
