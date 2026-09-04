from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


VALID_PREFIXES = (
    "https://d-nb.info",
    "https://www.wikidata.org",
    "https://www.geonames.org",
)


def collect_subject_uris_from_record(record: dict[str, Any]) -> list[str]:
    subject_uri = record.get("Subject_uri")
    if isinstance(subject_uri, list):
        return [str(item).strip() for item in subject_uri if str(item).strip()]
    if isinstance(subject_uri, str):
        return [subject_uri.strip()] if subject_uri.strip() else []
    return []


def is_target_url(url: str) -> bool:
    return url.startswith(VALID_PREFIXES)


def url_returns_404(url: str) -> bool:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.getcode() == 404
    except HTTPError as exc:
        return exc.code == 404
    except URLError:
        return False


def main() -> None:
    project_dir = Path(__file__).resolve().parent.parent
    data_dir = project_dir / "json_dumps_local"
    file_names = ["Persons.json", "Organizations.json", "Places.json"]
    broken_urls: list[dict[str, str]] = []

    for file_name in file_names:
        json_path = data_dir / file_name
        if not json_path.exists():
            print(f"Skipping missing file: {json_path}")
            continue

        with json_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            continue

        for record_id, record in data.items():
            if not isinstance(record, dict):
                continue

            for subject_url in collect_subject_uris_from_record(record):
                if not is_target_url(subject_url):
                    continue
                print(f"Checking URL: {subject_url}")
                if url_returns_404(subject_url):
                    broken_urls.append(
                        {
                            "file": file_name,
                            "id": str(record_id),
                            "Subject_uri": subject_url,
                        }
                    )

    output_path = project_dir / "404_subject_uris.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(broken_urls, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Checked {len(file_names)} files in {data_dir}")
    print(f"Found {len(broken_urls)} broken URLs")
    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()
