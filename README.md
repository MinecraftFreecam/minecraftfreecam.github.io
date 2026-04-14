# Freecam Website

Source for [minecraftfreecam.github.io](https://minecraftfreecam.github.io), [Freecam]'s landing page.

The site is built using [MkDocs] and managed using [uv].
Some content is pulled from the Freecam repository at build time, such as the project README.

## Prerequisites

- Python 3.12+
- [uv][uv-installation]
- A clone of [Freecam]

## Setup

Install dependencies:
```sh
uv sync
```

By default, the build expects some of Freecam's source files to be present at `./freecam`.
If `./freecam` is missing, `../freecam` and `../Freecam` are also checked, useful if you clone this repo alongside Freecam.

You can override the Freecam directory by setting the `FREECAM_DIR` environment variable:
```sh
export FREECAM_DIR=../Freecam
```

## Usage

**Local development** — builds and serves the site (with live reload):
```sh
uv run mkdocs serve
```

**Production build** — builds into `site/`:
```sh
uv run mkdocs build
```

**Lints** — you can run ruff, pytest, and mypy:
```sh
uv run ruff format
uv run ruff check
uv run pytest
uv run mypy .
```

## How it works

A [MkDocs hook](https://www.mkdocs.org/user-guide/configuration/#hooks) (`freecam_files.py`) runs at build time and:
- Reads `README.md` from the Freecam source, extracting sections marked with `<!-- website:start id="…" -->` and `<!-- website:end -->` tags
- Injects extracted content into `src/index.md` at `<!-- freecam:<id> -->` placeholders
- Exposes `metadata.toml` to MkDocs templates via page context

## CI

The site is built and deployed via GitHub Actions (`.github/workflows/build.yaml`).
Deployments happen on push to `main` and daily at ~6pm, to sync with upstream changes.
Deployment can also be triggered manually, against any Freecam ref.

[Freecam]: https://github.com/MinecraftFreecam/Freecam
[MkDocs]: https://www.mkdocs.org
[uv]: https://docs.astral.sh/uv
[uv-installation]: https://docs.astral.sh/uv/getting-started/installation

