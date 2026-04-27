import typer
from pathlib import Path
from typing import Annotated
from py_ssg_tools.icons import FontAwesome
from py_ssg_tools.fonts import GoogleFont
from py_ssg_tools.screenshots import Screenshotter

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
    subsets: Annotated[list[str] | None, typer.Option("--subset", help="Unicode subset to include (repeat for multiple, e.g. --subset latin --subset latin-ext). Default: all subsets.")] = None, # pyright: ignore[reportGeneralTypeIssues]
) -> None:
    GoogleFont(dest=dest).sync(font_names=names, weights=weights, subsets=subsets)


@app.command("screenshots")
def screenshots_cmd(
    base_url: str = typer.Option("http://127.0.0.1:1111", "--url", help="Base URL of the running Zola site"),
    dest: Path = typer.Option(..., "--dest", help="Destination directory for screenshots (relative to CWD)"),
    pages: Annotated[list[str] | None, typer.Option("--page", help='Page in "name:path" format (repeat for multiple, e.g. --page home:/ --page post:/posts/markdown/). Defaults to home and post pages.')] = None, # pyright: ignore[reportGeneralTypeIssues]
    themes: Annotated[list[str] | None, typer.Option("--theme", help="Themes to capture: dark, light (repeat for multiple). Defaults to both.")] = None, # pyright: ignore[reportGeneralTypeIssues]
    width: int = typer.Option(1320, "--width", help="Viewport width in pixels"),
    height: int = typer.Option(768, "--height", help="Viewport height in pixels"),
    device_scale_factor: float = typer.Option(2.0, "--scale", help="Device pixel ratio (2.0 = HiDPI/Retina)"),
) -> None:
    parsed_pages: list[dict] | None = None # pyright: ignore[reportGeneralTypeIssues]
    if pages:
        parsed_pages = []
        for entry in pages:
            if ":" not in entry:
                typer.echo(f"Invalid page format '{entry}'. Use 'name:path', e.g. 'home:/'", err=True)
                raise typer.Exit(1)
            name, path = entry.split(":", 1)
            parsed_pages.append({"name": name, "path": path})
    Screenshotter(base_url=base_url, dest=dest).capture(
        pages=parsed_pages,
        themes=themes if themes else None,
        width=width,
        height=height,
        device_scale_factor=device_scale_factor,
    )
