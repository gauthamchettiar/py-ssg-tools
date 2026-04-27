import json
import requests
from pathlib import Path


class FontAwesome:
    REPO_OWNER = "FortAwesome"
    REPO_NAME = "Font-Awesome"

    def __init__(self, dest: Path, version: str = "7.x", cache_file: Path | None = None) -> None: # pyright: ignore[reportGeneralTypeIssues]
        self.dest = dest
        self.version = version
        self.cache_file = cache_file or dest / "cache.json"

    def sync(self) -> None:
        print("Checking for icon updates...")
        remote_files = self._get_remote_tree()
        local_cache = self._load_cache()

        updated_count = 0
        new_count = 0

        for remote_path, remote_sha in remote_files.items():
            clean_path = remote_path.replace("svgs/", "", 1)
            local_path = self.dest / clean_path

            if local_cache.get(remote_path) != remote_sha or not local_path.exists():
                local_path.parent.mkdir(parents=True, exist_ok=True)

                raw_url = f"https://raw.githubusercontent.com/{self.REPO_OWNER}/{self.REPO_NAME}/{self.version}/{remote_path}"
                r = requests.get(raw_url)
                if r.status_code == 200:
                    local_path.write_bytes(r.content)

                    if remote_path in local_cache:
                        updated_count += 1
                    else:
                        new_count += 1

                    local_cache[remote_path] = remote_sha
                    print(f"Downloaded: {clean_path}")

        self._save_cache(local_cache)
        print(f"\nSync complete. New: {new_count}, Updated: {updated_count}")

    def _get_remote_tree(self) -> dict[str, str]:
        url = f"https://api.github.com/repos/{self.REPO_OWNER}/{self.REPO_NAME}/git/trees/{self.version}?recursive=1"
        response = requests.get(url)
        response.raise_for_status()
        tree = response.json().get("tree", [])
        return {
            item["path"]: item["sha"]
            for item in tree
            if item["path"].startswith("svgs/") and item["path"].endswith(".svg")
        }

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache: dict) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=2)