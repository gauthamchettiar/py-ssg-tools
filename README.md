# py-ssg-tools

A lightweight Python toolkit for static site tooling, bundled as a CLI under `pst` and managed with [uv](https://docs.astral.sh/uv/).

This project currently supports:

- `pst sync icons` — sync Font Awesome SVG icons from GitHub into a local repo directory.
- `pst sync fonts` — sync Google Fonts assets and generate local CSS with local font file references.

## Requirements

- Python 3.14+
- `uv` for dependency management and project execution

## Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies from pyproject.toml
uv sync
```

## Usage

All commands are exposed through the `pst` entrypoint:

```bash
uv run pst <command>
```

### Sync icons

Fetches SVG icons from the Font Awesome repository and writes them into the destination folder.

```bash
uv run pst sync icons --source font-awesome --dest <dest> [--version <version>]
```

Options:

- `--source` — Icon source name. Currently supported: `font-awesome`.
- `--dest` — Destination directory for downloaded SVG files.
- `--version` — Git tag or branch to sync from. Default: `7.x`.

Example:

```bash
uv run pst sync icons --source font-awesome --dest static/icons/fa/ --version 7.x
```

This command uses a cache file at `dest/cache.json` to avoid re-downloading unchanged icons.

### Sync fonts

Downloads Google Fonts `.woff2` files and rewrites the fetched CSS to point at the local font files.

```bash
uv run pst sync fonts --name "Open Sans" --name "Inter" --dest <dest> [--weights <weights>] [--subset <subset>...]
```

Options:

- `--name` — Font family name. Repeat this option to sync multiple fonts.
- `--dest` — Destination directory for the generated font files and CSS.
- `--weights` — Comma-separated font weights to request. Default: `400,700`.
- `--subset` — Unicode subset to include. Repeat for multiple subsets. If omitted, all subsets are used.

Example:

```bash
uv run pst sync fonts --name "Inter" --dest static/fonts --weights 400,700 --subset latin --subset latin-ext
```

For each font, the command creates a folder under `dest` and writes:

- `.woff2` font files
- a CSS file named after the font family

It also removes stale `.woff2` files that are no longer referenced by the current Google Fonts response.

## Project layout

- `pyproject.toml` — package metadata and dependencies
- `src/py_ssg_tools/cli.py` — Typer CLI entrypoint
- `src/py_ssg_tools/icons.py` — Font Awesome SVG sync implementation
- `src/py_ssg_tools/fonts.py` — Google Fonts sync implementation

## CI/CD example

Use `uv` in GitHub Actions to install dependencies and run the sync commands:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5

- name: Sync icons
  run: uv run pst sync icons --source font-awesome --dest static/icons/font-awesome/ --version 7.x

- name: Sync fonts
  run: uv run pst sync fonts --name "Inter" --dest static/fonts --weights 400,700 --subset latin
```
