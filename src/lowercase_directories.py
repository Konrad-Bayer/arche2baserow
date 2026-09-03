import json
from typing import Any


def lowercase_directory_paths(file_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Lowercase every directory value in a list of file entries."""
    for entry in file_list:
        if isinstance(entry, dict) and "directory" in entry and isinstance(entry["directory"], str):
            entry["directory"] = entry["directory"].lower()
    return file_list


def lowercase_filelist_json(json_path: str) -> list[dict[str, Any]]:
    """Load a JSON file and lowercase all directory values in place."""
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return lowercase_directory_paths(data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <json_path>")
        sys.exit(1)

    json_path = sys.argv[1]
    data = lowercase_filelist_json(json_path)
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Lowercased directory paths in {json_path}")
