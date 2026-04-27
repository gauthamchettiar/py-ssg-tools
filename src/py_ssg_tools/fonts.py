import hashlib
import json
import re
import requests
from pathlib import Path

class GoogleFont:
    CSS_API_URL = "https://fonts.googleapis.com/css2"

    def __init__(self, dest: Path, cache_file: Path | None = None) -> None: # pyright: ignore[reportGeneralTypeIssues]
        self.dest = dest
        self.cache_file = cache_file or dest / "cache.json"

    def sync(self, font_names: list[str], weights: str = "400,700", subsets: list[str] | None = None) -> None:
        local_cache = self._load_cache()
        for font_name in font_names:
            self._sync_one(font_name, weights, subsets, local_cache)
        self._save_cache(local_cache)

    def _sync_one(self, font_name: str, weights: str, subsets: list[str] | None, local_cache: dict) -> None:
        print(f"Checking for {font_name} updates...")

        family = font_name.replace(" ", "+")
        gf_weights = weights.replace(",", ";")
        url = f"{self.CSS_API_URL}?family={family}:wght@{gf_weights}&display=swap"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch CSS for {font_name}. Check the spelling.")
            return

        css_content = response.text
        blocks = self._parse_font_faces(css_content)

        if subsets:
            allowed = {s.lower() for s in subsets}
            blocks = [b for b in blocks if b["subset"].lower() in allowed]

        if not blocks:
            print(f"No font files found for {font_name}. Check the requested weights/subsets.")
            return

        font_slug = font_name.lower().replace(" ", "-")
        font_dir_name = font_name.replace(" ", "_")
        font_dir = self.dest / font_dir_name
        font_dir.mkdir(parents=True, exist_ok=True)

        updated_count = 0
        new_count = 0
        url_to_local: dict[str, str] = {}
        expected_files: set[str] = set()

        for block in blocks:
            font_url = block["url"]
            readable_name = self._make_filename(font_slug, block)
            local_path = font_dir / readable_name
            url_to_local[font_url] = f"./{readable_name}"
            expected_files.add(readable_name)

            cached_hash = local_cache.get(font_url)
            local_hash = hashlib.sha256(local_path.read_bytes()).hexdigest() if local_path.exists() else None

            if cached_hash is None or local_hash != cached_hash:
                r = requests.get(font_url)
                if r.status_code == 200:
                    content = r.content
                    new_hash = hashlib.sha256(content).hexdigest()
                    local_path.write_bytes(content)
                    if font_url in local_cache:
                        updated_count += 1
                    else:
                        new_count += 1
                    local_cache[font_url] = new_hash
                    print(f"Downloaded: {readable_name}")

        # Remove stale files no longer part of the current sync
        for stale in font_dir.glob("*.woff2"):
            if stale.name not in expected_files:
                stale.unlink()
                print(f"Removed stale: {stale.name}")

        # Rewrite CSS with local readable paths
        local_css = css_content
        for remote_url, local_rel in url_to_local.items():
            local_css = local_css.replace(f"url({remote_url})", f"url({local_rel})")

        css_path = font_dir / f"{font_dir_name}.css"
        css_path.write_text(local_css)
        print(f"Written: {font_dir_name}/{css_path.name}")
        print(f"Sync complete for {font_name}. New: {new_count}, Updated: {updated_count}")

    def _parse_font_faces(self, css: str) -> list[dict]:
        pattern = re.compile(r"/\*\s*([^*]+?)\s*\*/\s*@font-face\s*\{([^}]+)\}", re.DOTALL)
        results = []
        for m in pattern.finditer(css):
            subset = m.group(1).strip()
            block_body = m.group(2)
            weight_m = re.search(r"font-weight:\s*(\d+)", block_body)
            style_m = re.search(r"font-style:\s*(\w+)", block_body)
            url_m = re.search(r"src:\s*url\(([^)]+)\)", block_body)
            if not url_m:
                continue
            results.append({
                "subset": subset,
                "weight": weight_m.group(1) if weight_m else "400",
                "style": style_m.group(1) if style_m else "normal",
                "url": url_m.group(1),
            })
        return results

    def _make_filename(self, font_slug: str, block: dict) -> str:
        subset = block["subset"].replace(" ", "-")
        parts = [font_slug, block["weight"]]
        if block["style"] != "normal":
            parts.append(block["style"])
        parts.append(subset)
        return "-".join(parts) + ".woff2"

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache: dict) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=2)
