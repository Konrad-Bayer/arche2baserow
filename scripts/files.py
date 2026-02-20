import os
import glob
import json
import re
# import locale                     

from datetime import datetime
from tqdm import tqdm
from template import COLLECTION_SUB, RESOURCE_SUB
from utils.baserow import create_id_list
from typing import TypedDict

# locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

konrad_bayer_uri = "https://d-nb.info/gnd/118507753/"

entity_str_replace = {
    "an bayer konrad": "an Bayer, Konrad",
    "an bayer traudl": "an Bayer, Traudl",
    "an bayer": "an Bayer, Konrad",
    "von bayer traudl": "von Bayer, Traudl",
    "von bayer konrad": "von Bayer, Konrad",
}


def natural_key(path: str) -> list[int | str]:
    name = os.path.basename(path)
    parts = re.split(r'(\d+)', name)
    # convert digit parts to int, keep non-digits as lower-case strings
    return [int(p) if p.isdigit() else p.lower() for p in parts]


class DataItem(TypedDict, total=False):
    name: str
    identifier: str
    author: str | None
    actor: str | None
    date: str | None
    title: str | None
    isPartOf: str
    page: str | None
    collection: str
    type: str
    hasNextItem: str | None
    path: str


def _parse_collection_directory(
        item: str,
        name: str,
        name_list: list[str]) -> tuple[str, str | None, str | None, str | None, str | None]:

    """Extract collection, identifier, title, author, actor from directory name."""

    collection = None
    identifier = None
    title = None
    author = None
    actor = None
    date = None

    if "_briefe" in name or "_mappen" in name:
        identifier = "_".join(name_list[0:3]) if len(name_list) > 2 else name_list[0]
        title = name_list[2] if len(name_list) > 2 else name_list[1]
        collection = "korrespondenz"
    elif "Korrespondenz" in item:
        identifier = name_list[0]
        author = name_list[1]
        actor = name_list[2]
        date = name_list[3] if len(name_list) > 3 and name_list[3].startswith("19") else None
        title = name_list[3] if not date and len(name_list) > 3 else None
        if len(name_list) > 4 and title:
            title += "_" + "_".join(name_list[4:])
        collection = "korrespondenz"
    else:
        identifier = name_list[0]
        title = name_list[1]
        date = title.split("-")[1] if "-" in title else None
        collection = "kalender"

    return collection, identifier, title, author, actor, date


def _create_data_item(name: str, identifier: str, is_part_of: str, item_type: str, **kwargs) -> DataItem:
    """Factory function to create consistent DataItem objects."""
    return {
        "name": name,
        "identifier": identifier,
        "author": kwargs.get("author"),
        "actor": kwargs.get("actor"),
        "date": kwargs.get("date"),
        "title": kwargs.get("title"),
        "isPartOf": is_part_of.lower(),
        "page": kwargs.get("page"),
        "collection": kwargs.get("collection"),
        "type": item_type,
        "hasNextItem": kwargs.get("hasNextItem"),
        "path": kwargs.get("path"),
    }


def list_directories_or_files(path: str, data: list) -> list[DataItem]:
    """List all directories or files in a given path."""
    content = sorted(glob.glob(os.path.join(path, "*")), key=natural_key)

    for idx, item in enumerate(tqdm(content, total=len(content))):
        name = os.path.basename(item)
        name_list = name.split("_")
        is_part_of = os.path.dirname(item).split("/")[-1]
        is_part_of = "kalender" if is_part_of == "Taschenkalender" else is_part_of

        if len(name_list) <= 1:
            list_directories_or_files(item, data)
            continue

        print(f"Processing: {name}")
        next_item = content[idx + 1] if idx + 1 < len(content) else None
        next_item_name = os.path.basename(next_item) if next_item else None

        if os.path.isdir(item):
            collection, identifier, title, author, actor, date = _parse_collection_directory(item, name, name_list)
            first_child = sorted(glob.glob(os.path.join(item, "*")), key=natural_key)
            has_next_item = os.path.basename(first_child[0]) if first_child else None

            if author and actor:
                author = " ".join(author.split("-"))
                actor = " ".join(actor.split("-"))

            data_item = _create_data_item(
                name, identifier, is_part_of, "Collection",
                author=author, actor=actor, title=title, date=date,
                collection=collection, hasNextItem=has_next_item, path=item
            )
            data.append(data_item)
            list_directories_or_files(item, data)

        elif os.path.isfile(item):
            collection = "korrespondenz" if "Korrespondenz" in item else "kalender"
            page_offset = 2 if collection == "korrespondenz" else 3
            page = "_".join(name_list[page_offset:]).replace(".tiff", "")
            identifier = f"{name_list[1]}/{name}"

            data_item = _create_data_item(
                name, identifier, name_list[1], "Resource",
                collection=collection, page=page, hasNextItem=next_item_name, path=item
            )
            data.append(data_item)

    return data


class TemplateItem(TypedDict):
    id: int
    Subject_uri: str
    Class: list[int]
    Predicate_uri: list[int]
    Object_uri_persons: list[int]
    Object_uri_places: list[int]
    Object_uri_organizations: list[int]
    Object_uri_resource: list[int]
    Object_uri_vocabs: list[int]
    Literal: str | None
    Language: str | None
    Date: str | None
    Number: int | None
    Inherit: list[int]


def _create_template_item(ids: int, uri: str, classes_name: str, prop: str,
                          default_properties: list[dict], default_classes: list[dict],
                          literal: str | None = None, date: str | None = None,
                          lang: str | None = None, object_uri_vocabs: list[int] = []) -> TemplateItem:
    """Factory function to create consistent TemplateItem objects."""
    return {
        "id": ids,
        "Subject_uri": uri,
        "Class": create_id_list(default_classes, classes_name),
        "Predicate_uri": create_id_list(default_properties, prop),
        "Object_uri_persons": [],
        "Object_uri_places": [],
        "Object_uri_organizations": [],
        "Object_uri_resource": [],
        "Object_uri_vocabs": object_uri_vocabs,
        "Literal": literal,
        "Language": lang,
        "Date": date,
        "Number": None,
        "Inherit": []
    }


def create_template_lists(ids: int,
                          custom_properties: list[str],
                          classes_name: str,
                          default_properties: list[dict],
                          default_classes: list[dict],
                          item: dict = None):
    template = []
    if item["collection"] != item["isPartOf"]:
        uri_path = f"{item['collection']}/{item['isPartOf']}"
    else:
        uri_path = item['isPartOf']
    uri = f"{item['collection']}/{item['identifier']}"
    for prop in custom_properties:
        literal = ""
        date = None
        # hasNextItem
        if prop == "hasNextItem" and item["hasNextItem"]:
            literal = []
            literal.append(item["collection"])
            if item["type"] == "Resource":
                literal.append(item["isPartOf"])
            if item["type"] == "Collection":
                literal.append(item["identifier"])
            literal.append(item["hasNextItem"])
            literal = "/".join(literal)
        # hasAuthor and hasActor
        if prop == "hasAuthor" or prop == "hasActor":
            literal = f"{item['author']} - {item['actor']}" if item["author"]\
                and item["actor"] else None
        # hasTitle
        if prop == "hasTitle":
            if item["collection"] == "kalender":
                if item["type"] == "Collection":
                    literal = item["title"].split("-")[0] if item["title"] else ""
                    literal = f"{literal[0][0].upper()}{literal[0][1:]} {literal[1:]}"
                else:
                    literal = item['page'] if item['page'] else ""
            else:
                if item["type"] == "Collection":
                    author = entity_str_replace.get(item['author'], item['author'])\
                        if item['author'] else ""
                    actor = entity_str_replace.get(item['actor'], item['actor'])\
                        if item['actor'] else ""
                    date_str = ""
                    if item['date']:
                        # Year-only
                        if len(item['date']) == 4:
                            try:
                                date_str = datetime.strptime(item['date'], "%Y")
                            except ValueError:
                                date_str = item['date']
                        # Likely full date (try ISO first, then verbose formats)
                        elif len(item['date']) == 10:
                            # convert to datetime object if possible, then format as "17. Juli 1955"
                            # locale must be de_DE for German month names
                            try:
                                date_str = datetime.fromisoformat(item['date'])
                                date_str = date_str.strftime("%d. %B %Y")
                            except ValueError:
                                date_str = item['date']
                    literal = f"Korrespondenz {author} {actor} am {date_str}{item['title'] if item['title'] else ""}"
                else:
                    literal = item['page'] if item['page'] else ""
        # isPartOf
        if prop == "isPartOf":
            literal = uri_path
        # hasTag
        if prop == "hasTag":
            literal = "TEXT"
        # hasOaiSet
        if prop == "hasOaiSet":
            object_uri_vocabs = [87]
        else:
            object_uri_vocabs = []
        # Dates
        if prop == "hasCoverageStartDate":
            if item["date"] and len(item["date"]) == 4:
                date = f"{item['date']}-01-01"
            else:
                date = item["date"] if item["date"] else ""
        if prop == "hasCoverageEndDate":
            if item["date"] and len(item["date"]) == 4:
                date = f"{item['date']}-12-31"
            else:
                date = item["date"] if item["date"] else ""
        # hasLanguage
        if prop == "hasLanguage":
            lang = "de"
        else:
            lang = ""
        print(f"Creating {prop} template...")

        template.append(_create_template_item(
            ids, uri, classes_name, prop, default_properties, default_classes,
            literal=literal, date=date, lang=lang, object_uri_vocabs=object_uri_vocabs
        ))

        ids += 1
    return ids, template


def load_properties_and_classes():
    with open("out/properties.json", "r") as f:
        properties: list[dict] = json.load(f)
    with open("out/classes.json", "r") as f:
        classes: list[dict] = json.load(f)
    return properties, classes


def align_files_with_template(files: list[dict], template: list,
                              key: str) -> list[dict]:
    properties, classes = load_properties_and_classes()
    return_list = []
    ids = 0
    for file in files:
        ids_update, custom_template_project = create_template_lists(
            ids,
            template,
            key,
            properties,
            classes,
            file
        )
        ids = ids_update
        return_list.extend(custom_template_project)
    return return_list


def extract_data_from_files():
    share = "/mnt/acdh_arche"
    archeDir = "/ACDH_ARCHE/staging"
    projectDir = "/KonradBayer_27121/data/KB_2026_Digitale_Transformation"
    path = f"{share}{archeDir}{projectDir}"
    data = list_directories_or_files(path, [])
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Data saved to data.json")


def create_arche_baserow():
    with open("data.json", "r") as f:
        data = json.load(f)

    collection_data = [item for item in data if item["type"] == "Collection"]
    resource_data = [item for item in data if item["type"] == "Resource"]

    cols = align_files_with_template(collection_data,
                                     COLLECTION_SUB,
                                     "Collection")
    res = align_files_with_template(resource_data,
                                    RESOURCE_SUB,
                                    "Resource")

    with open("cols.json", "w") as f:
        json.dump(cols, f, indent=4)
    with open("res.json", "w") as f:
        json.dump(res, f, indent=4)

    print("Collection and Resource data saved to cols.json and res.json")


def chunk_list(items: list, size: int = 50):
    """Yield successive chunks (lists) of length `size` from `items`."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


if __name__ == "__main__":
    extract_data_from_files()
    create_arche_baserow()
    # with open("cols.json", "r") as f:
    #     cols = json.load(f)
    # with open("res.json", "r") as f:
    #     res = json.load(f)

    # os.makedirs("chunks", exist_ok=True)
    # cols_chunks = list(chunk_list(cols, 100))
    # for idx, chunk in enumerate(cols_chunks, start=1):
    #     fname = f"chunks/cols_chunk_{idx}.json"
    #     with open(fname, "w") as f:
    #         json.dump(chunk, f, indent=2)
    #     # upload chunk to Baserow (table id as needed)
    #     update_table_rows_batch("5194", chunk)
    #     sleep(3)

    # res_chunks = list(chunk_list(res, 100))
    # for idx, chunk in enumerate(res_chunks, start=1):
    #     fname = f"chunks/res_chunk_{idx}.json"
    #     with open(fname, "w") as f:
    #         json.dump(chunk, f, indent=2)
    #     update_table_rows_batch("5195", chunk)
    #     sleep(3)

    print("Data uploaded to Baserow")
