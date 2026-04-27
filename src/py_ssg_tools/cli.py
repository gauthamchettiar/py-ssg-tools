import typer
from pathlib import Path
from typing import Annotated
from py_ssg_tools.icons import FontAwesome
from py_ssg_tools.fonts import GoogleFont

app = typer.Typer()
sync_app = typer.Typer()
app.add_typer(sync_app, name="sync")

_SOURCES = {
    "font-awesome": FontAwesome,
}


@sync_app.command("icons")
def icons(
    source: str = typer.Option(..., "--source", help=f"Icon source. Available: {', '.join(_SOURCES)}"),
    dest: Path = typer.Option(..., "--dest", help="Destination directory (relative to CWD)"),
    version: str = typer.Option("7.x", "--version", help="Branch or version tag"),
) -> None:
    if source not in _SOURCES:
        typer.echo(f"Unknown source '{source}'. Available: {', '.join(_SOURCES)}", err=True)
        raise typer.Exit(1)
    _SOURCES[source](dest=dest, version=version).sync()


@sync_app.command("fonts")
def fonts(
    names: Annotated[list[str], typer.Option("--name", help="Font family name (repeat for multiple)")],
    dest: Path = typer.Option(..., "--dest", help="Destination directory (relative to CWD)"),
    weights: str = typer.Option("400,700", "--weights", help="Comma-separated font weights (e.g. 400,700)"),
    subsets: Annotated[list[str] | None, typer.Option("--subset", help="Unicode subset to include (repeat for multiple, e.g. --subset latin --subset latin-ext). Default: all subsets.")] = None,
) -> None:
    GoogleFont(dest=dest).sync(font_names=names, weights=weights, subsets=subsets)
