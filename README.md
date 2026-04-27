# yolk-scripts

Helper scripts for the `zola-yolk` theme, exposed via the `pst` CLI. Managed with [uv](https://docs.astral.sh/uv/).

## Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd scripts
uv sync
```

## Usage

### `pst sync icons`

Downloads SVG icons from a remote source into a local directory, using a cache to skip unchanged files.

```
uv run pst sync icons --source <source> --dest <dest> [--version <version>]
```

| Option | Description | Default |
|---|---|---|
| `--source` | Icon source (see below) | required |
| `--dest` | Destination directory (relative to CWD) | required |
| `--version` | Branch or version tag | `7.x` |

**Available sources:**

| Source | Description |
|---|---|
| `font-awesome` | Font Awesome SVGs from the official GitHub repo |

**Example** (from `zola-yolk/` root):

```bash
uv --project scripts run pst sync icons --source font-awesome --dest static/icons/fa/ --version 7.x
```

## CI/CD

In a GitHub Actions workflow:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5

- name: Sync icons
  run: uv --project scripts run pst sync icons --source font-awesome --dest static/icons/font-awesome/ --version 7.x
```
