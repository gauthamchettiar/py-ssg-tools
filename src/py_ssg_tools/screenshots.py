from playwright.sync_api import sync_playwright # type: ignore
from pathlib import Path

_DEFAULT_PAGES = [
    {"name": "home", "path": "/"},
    {"name": "post", "path": "/posts/markdown/"},
]

_DEFAULT_THEMES = ["dark", "light"]


class Screenshotter:
    def __init__(self, base_url: str, dest: Path) -> None:
        self.base_url = base_url.rstrip("/")
        self.dest = dest

    def capture(
        self,
        pages: list[dict] | None = None, # pyright: ignore[reportGeneralTypeIssues]
        themes: list[str] | None = None, # pyright: ignore[reportGeneralTypeIssues]
        width: int = 1320,
        height: int = 768,
        device_scale_factor: float = 2.0,
    ) -> None:
        pages = pages if pages is not None else _DEFAULT_PAGES
        themes = themes if themes is not None else _DEFAULT_THEMES

        self.dest.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            for page_config in pages:
                name = page_config["name"]
                path = page_config.get("path", "/")
                for theme in themes:
                    pg = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=device_scale_factor)
                    # Pre-set localStorage so the inline theme script picks it up on load
                    pg.add_init_script(f"localStorage.setItem('theme', '{theme}')")
                    pg.goto(f"{self.base_url}{path}", wait_until="load")
                    out_path = self.dest / f"{name}-{theme}.png"
                    pg.locator("body").screenshot(path=str(out_path))
                    print(f"Captured: {out_path}")
                    pg.close()
            browser.close()
