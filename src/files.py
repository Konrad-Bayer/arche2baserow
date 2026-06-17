import os
import glob
import json
import re

# from datetime import datetime
from tqdm import tqdm
from template import COLLECTION_SUB, RESOURCE_SUB
from utils.baserow import create_id_list, create_database_table, update_table_field_types, update_table_rows_batch
from time import sleep
from typing import TypedDict
from config import (jwt_token, BASEROW_DB_ID, PROJECT_NAME)


# Baserow Collection and Resource table template fields
default_fields = [
    {"name": "Subject_uri", "type": "text"},
    {
        "name": "Class",
        "type": "link_row",
        "link_row_table_id": 5197,
        "has_related_field": False
    },
    {
        "name": "Predicate_uri",
        "type": "link_row",
        "link_row_table_id": 5198,
        "has_related_field": False
    },
    {
        "name": "Object_uri_persons",
        "type": "link_row",
        "link_row_table_id": 5199,
        "has_related_field": False
    },
    {
        "name": "Object_uri_places",
        "type": "link_row",
        "link_row_table_id": 5200,
        "has_related_field": False
    },
    {
        "name": "Object_uri_organizations",
        "type": "link_row",
        "link_row_table_id": 5201,
        "has_related_field": False
    },
    {
        "name": "Object_uri_resource",
        "type": "link_row",
        "link_row_table_id": 5202,
        "has_related_field": False
    },
    {
        "name": "Object_uri_vocabs",
        "type": "link_row",
        "link_row_table_id": 5196,
        "has_related_field": False
    },
    {"name": "Literal", "type": "text"},
    {"name": "Language", "type": "text"},
    {"name": "Date", "type": "text"},
    {"name": "Number", "type": "number"},
    {
        "name": "Inherit",
        "type": "link_row",
        "link_row_table_id": 5197,
        "has_related_field": False
    }
]


def create_template_lists(ids: int,
                          custom_properties: list[str],
                          classes_name: str,
                          default_properties: list[dict],
                          default_classes: list[dict],
                          item: dict = None):
    template = []
    uri_path = item['isPartOf']
    uri = item['identifier']

    for prop in custom_properties:
        literal = ""
        lang = ""
        date = ""
        object_uri_persons = []
        object_uri_vocabs = []
        object_uri_places = []
        object_uri_organizations = []
        inherit = []
        number = None

        # case statements for specific properties to handle their values
        match prop:
            case "hasActor":
                if item["type"] == "Collection":
                    if item["collection"] == "korrespondenz":
                        object_uri_persons = item["actor_pers"] + item["author_pers"]
                        object_uri_organizations = item["actor_org"] + item["author_org"]
                    else:
                        object_uri_persons = [1]  # Konrad Bayer
                else:
                    if item["collection"] == "korrespondenz":
                        object_uri_persons = item["actor_pers"]
                        object_uri_organizations = item["actor_org"]

            case "hasAuthor":
                if item["collection"] == "korrespondenz":
                    object_uri_persons = item["author_pers"]
                    object_uri_organizations = item["author_org"]
                else:
                    object_uri_persons = [1]  # Konrad Bayer

            case "hasRightsHolder":
                if item["collection"] == "kalender":
                    object_uri_organizations = [2]  # Blaues Laub

            case "hasLicensor":
                if item["collection"] == "kalender":
                    object_uri_organizations = [2]  # Blaues Laub

            case "hasLicense":
                object_uri_vocabs = [56]  # CC BY 4.0

            case "hasCategory":
                object_uri_vocabs = [2]  # Konrad Bayer

            case "hasDigitisingAgent":
                object_uri_organizations = [2]  # Blaues Laub

            case "hasAccessRestriction":
                object_uri_vocabs = [41]

            case "hasFormat":
                literal = "image/tiff"

            case "hasFileName":
                literal = item['name']

            case "hasCreator":
                object_uri_persons = [4, 5]  # Julius, Sandro

            case "hasMetadataCreator":
                object_uri_persons = [4, 5]  # Julius, Sandro

            case "hasOwner":
                object_uri_organizations = [1]  # ÖAW

            case "hasSubject":
                if item["collection"] == "korrespondenz":
                    literal = "Korrespondenzen"
                else:
                    literal = "Kalender, Taschenkalender"

            case "hasTag":
                literal = "TEXT"

            case "isPartOf":
                literal = uri_path

            case "hasOaiSet":
                object_uri_vocabs = [87]

            case "hasNextItem":
                if item["hasNextItem"]:
                    literal = []
                    # literal.append(item["collection"])
                    if item["type"] == "Resource":
                        literal.append(item["isPartOf"])
                    if item["type"] == "Collection":
                        literal.append(item["identifier"])
                    literal.append(item["hasNextItem"])
                    literal = "/".join(literal)

            case "hasTitle":
                if item["type"] == "Collection":
                    literal = " ".join(" ".join(item["title"].split("_")).split("-"))
                else:
                    is_part_of = " ".join(" ".join(item["isPartOf"].split("/")[-1].split("_")).split("-"))
                    page = item['page'] if item['page'] else ""
                    literal = f"{is_part_of} {page}".strip()

            case "hasCoverageStartDate":
                if item["date"]:
                    if len(item["date"]) == 4:
                        date = f"{item['date']}-01-01"
                    else:
                        date = item["date"]
                    inherit = [48]

            case "hasCoverageEndDate":
                if item["date"]:
                    if len(item["date"]) == 4:
                        date = f"{item['date']}-12-31"
                    else:
                        date = item["date"]
                    inherit = [48]

            case "hasLanguage":
                object_uri_vocabs = [3949]  # deu

        print(f"Creating {prop} template...")

        template.append(_create_template_item(
            ids, uri, classes_name, prop, default_properties, default_classes,
            literal=literal, date=date, lang=lang, object_uri_vocabs=object_uri_vocabs,
            object_uri_persons=object_uri_persons, object_uri_places=object_uri_places,
            object_uri_organizations=object_uri_organizations, inherit=inherit, number=number
        ))

        ids += 1
    return ids, template


def natural_key(path: str) -> list[int | str]:
    """Generate a key for natural sorting of file paths.

    Args:
        path (str): file path to be sorted

    Returns:
        list[int | str]: list of integers and strings for natural sorting
    """
    name = os.path.basename(path)
    parts = re.split(r'(\d+)', name)
    # convert digit parts to int, keep non-digits as lower-case strings
    return [int(p) if p.isdigit() else p.lower() for p in parts]


class DataItem(TypedDict, total=False):
    name: str
    identifier: str
    author_pers: list[str] | None
    author_org: list[str] | None
    actor_pers: list[str] | None
    actor_org: list[str] | None
    date: str | None
    title: str | None
    isPartOf: str
    page: str | None
    collection: str
    type: str
    hasNextItem: str | None
    path: str


def _create_data_item(
    name: str,
    identifier: str,
    is_part_of: str,
    item_type: str,
    **kwargs
) -> DataItem:
    """Factory function to create consistent DataItem objects."""

    return {
        "name": name,
        "identifier": identifier,
        "isPartOf": is_part_of.lower(),
        "type": item_type,
        "author_pers": kwargs.get("author_pers"),
        "author_org": kwargs.get("author_org"),
        "actor_pers": kwargs.get("actor_pers"),
        "actor_org": kwargs.get("actor_org"),
        "date": kwargs.get("date"),
        "title": kwargs.get("title"),
        "page": kwargs.get("page"),
        "collection": kwargs.get("collection"),
        "hasNextItem": kwargs.get("hasNextItem"),
        "path": kwargs.get("path"),
    }


def _parse_collection_directory(
        item: str,
        name: str,
        name_list: list[str]) -> tuple[str, str | None, str | None, str | None, str | None]:

    """Extract collection, identifier, title, author, actor from directory name."""

    collection = None
    identifier = None
    author = None
    actor = None
    date = None
    title = name

    # Handle first sub collections of correspondenzes
    if "Korrespondenz" in name or "korrespondenz" in name:
        collection = "korrespondenz"
        author, actor = get_actor_author_from_name_list(name_list, wrapper=True)

    # Handle collection representing the letter itself
    elif "Korrespondenz" in item:
        collection = "korrespondenz"
        author, actor = get_actor_author_from_name_list(name_list)

    # everything is is part of the calendar collection
    else:
        collection = "kalender"
        date = name.split("-")[-1] if "-" in name else None

    identifier = f"{PROJECT_NAME}/{collection}/{name.lower()}"

    return collection, identifier, title, author, actor, date


def get_actor_author_from_name_list(name_list: list[str], wrapper: bool = False) -> tuple[str | None, str | None]:
    """Extract actor and author from a given name list."""
    author = None
    actor = None

    if len(name_list) > 2:
        if wrapper:  # correspondences between two poeple is wrapped in a directory
            author = name_list[1]
            actor = name_list[2]

        else:  # correspondence collection or resource
            author = name_list[0]
            actor = name_list[1]

            # first item in dir name before _ is expected to be the author
            #  e.g. "von-bayer-konrad_an-traudl_1930-01-01"; except if it starts with "an-"
            if author and author.startswith("an-"):
                author = name_list[1]
                actor = name_list[0]

    else:
        with open("logs_letter_collection.txt", "a") as log_file:
            log_file.write(f"Unexpected directory name format: {'_'.join(name_list)}\n")

    return author, actor


def list_directories_or_files(
    path: str,
    data: list,
    persons_dict: dict = {},
    organizations_dict: dict = {}
) -> list[DataItem]:
    """List all directories or files in a given path."""

    content = sorted(glob.glob(os.path.join(path, "*")), key=natural_key)

    for idx, item in enumerate(tqdm(content, total=len(content))):
        name = os.path.basename(item)
        if name == "NOCH_ZUZUORDNENDES_MATERIAL":
            continue  # directory of unassigned material, skip it
        name_list = name.split("_")
        is_part_of = os.path.dirname(item).split("/")[-1].strip()
        is_part_of = "kalender" if is_part_of == "Taschenkalender" else is_part_of.lower()

        if len(name_list) <= 1:
            list_directories_or_files(item, data, persons_dict=persons_dict, organizations_dict=organizations_dict)
            continue

        print(f"Processing: {name}")
        next_item = content[idx + 1] if idx + 1 < len(content) else None
        next_item_name = os.path.basename(next_item).strip() if next_item else None

        author_pers = []
        author_org = []
        actor_pers = []
        actor_org = []

        if os.path.isdir(item):
            collection, identifier, title, author, actor, date = _parse_collection_directory(item, name, name_list)
            first_child = sorted(glob.glob(os.path.join(item, "*")), key=natural_key)
            has_next_item = os.path.basename(first_child[0]).strip() if first_child else None
            is_part_of = f"{PROJECT_NAME}/{collection}/{is_part_of}" if is_part_of != "kalender"\
                and is_part_of != "korrespondenz" else f"{PROJECT_NAME}/{collection}"

            # author actor handling
            actor_pers, author_pers, actor_org, author_org = get_actor_author_from_name(
                author, actor, persons_dict, organizations_dict
            )

            data_item = _create_data_item(
                name, identifier, is_part_of, "Collection",
                author_pers=author_pers, author_org=author_org, actor_pers=actor_pers,
                actor_org=actor_org, title=title, date=date,
                collection=collection, hasNextItem=has_next_item, path=item
            )

            data.append(data_item)
            list_directories_or_files(item, data, persons_dict=persons_dict, organizations_dict=organizations_dict)

        elif os.path.isfile(item):
            if ".tiff" not in name.lower():
                continue

            collection = "korrespondenz" if "Korrespondenz" in item else "kalender"
            page_offset = 2 if collection == "korrespondenz" else 3
            page = "_".join(name_list[page_offset:]).replace(".tiff", "")
            identifier = f"{PROJECT_NAME}/{collection}/{is_part_of}/{name}"
            is_part_of = f"{PROJECT_NAME}/{collection}/{is_part_of}"

            # author and actor handling
            parent_dir = os.path.dirname(item)
            parent_name = os.path.basename(parent_dir)
            parent_name_list = parent_name.split("_")

            if collection == "korrespondenz":
                author, actor = get_actor_author_from_name_list(parent_name_list)

                actor_pers, author_pers, actor_org, author_org = get_actor_author_from_name(
                    author, actor, persons_dict, organizations_dict
                )

            data_item = _create_data_item(
                name, identifier, is_part_of, "Resource", author_pers=author_pers, author_org=author_org,
                actor_pers=actor_pers, actor_org=actor_org,
                collection=collection, page=page, hasNextItem=next_item_name, path=item
            )
            data.append(data_item)

    return data


def get_actor_author_from_name(
    author: str,
    actor: str,
    persons_dict: dict,
    organizations_dict: dict
) -> tuple[list[int], list[int], list[int], list[int]]:
    """Extract actor and author IDs from a given name using provided dictionaries."""

    author_pers = []
    author_org = []
    actor_pers = []
    actor_org = []

    if author:
        entry_pers = persons_dict.get(author.lower())
        entry_org = organizations_dict.get(author.lower())
        if entry_pers:
            author_pers.append(entry_pers)
        if entry_org:
            author_org.append(entry_org)

    if actor:
        entry_pers = persons_dict.get(actor.lower())
        entry_org = organizations_dict.get(actor.lower())
        if entry_pers:
            actor_pers.append(entry_pers)
        if entry_org:
            actor_org.append(entry_org)

    return actor_pers, author_pers, actor_org, author_org


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


def _create_template_item(
    ids: int,
    uri: str,
    classes_name: str,
    prop: str,
    default_properties: list[dict],
    default_classes: list[dict],
    **kwargs
) -> TemplateItem:
    """Factory function to create consistent TemplateItem objects."""

    return {
        "id": ids,
        "Subject_uri": uri,
        "Class": create_id_list(default_classes, classes_name),
        "Predicate_uri": create_id_list(default_properties, prop),
        "Object_uri_persons": kwargs.get("object_uri_persons", []),
        "Object_uri_places": kwargs.get("object_uri_places", []),
        "Object_uri_organizations": kwargs.get("object_uri_organizations", []),
        "Object_uri_resource": kwargs.get("object_uri_resource", []),
        "Object_uri_vocabs": kwargs.get("object_uri_vocabs", []),
        "Literal": kwargs.get("literal", ""),
        "Language": kwargs.get("lang", ""),
        "Date": kwargs.get("date", ""),
        "Number": kwargs.get("number", None),
        "Inherit": kwargs.get("inherit", [])
    }


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


def extract_data_from_files(persons_dict: dict, organizations_dict: dict) -> list[dict]:

    share = "/mnt/projects01"
    archeDir = "/ACDH_ARCHE/staging"
    projectDir = "/KonradBayer_27121/data/KB_2026_Digitale_Transformation"
    path = f"{share}{archeDir}{projectDir}"
    data = list_directories_or_files(path, [], persons_dict=persons_dict, organizations_dict=organizations_dict)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Data saved to data.json")

    return data


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
    return cols, res


def chunk_list(items: list, size: int = 50):
    """Yield successive chunks (lists) of length `size` from `items`."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def entities_dict(entities: dict[str, dict]) -> dict[str, int]:
    """Create a dictionary mapping entity names to their IDs."""
    dict_entity = {}

    for entity in entities.values():
        labels = entity["id_to_string"].split(",") if entity["id_to_string"] else []
        if labels:
            for label in labels:
                dict_entity[label.strip()] = entity["id"]

    return dict_entity


if __name__ == "__main__":
    with open("json_dumps/Persons.json", "r") as f:
        persons = json.load(f)
    person_dict = entities_dict(persons)

    with open("json_dumps/Organizations.json", "r") as f:
        organizations = json.load(f)
    organization_dict = entities_dict(organizations)

    data = extract_data_from_files(
        persons_dict=person_dict,
        organizations_dict=organization_dict)
    cols, res = create_arche_baserow()

    collections = create_database_table(
        BASEROW_DB_ID,
        jwt_token,
        "Collections",
        "Subject_uri"
    )
    sleep(3)
    resources = create_database_table(
        BASEROW_DB_ID,
        jwt_token,
        "Resources",
        "Subject_uri"
    )

    sleep(3)
    update_table_field_types(
        collections["id"],
        jwt_token,
        default_fields
    )
    sleep(3)
    update_table_field_types(
        resources["id"],
        jwt_token,
        default_fields
    )
    sleep(3)

    sample = 100
    os.makedirs("chunks", exist_ok=True)
    cols_chunks = list(chunk_list(cols, 100))
    for idx, chunk in enumerate(cols_chunks[:sample], start=1):
        fname = f"chunks/cols_chunk_{idx}.json"
        with open(fname, "w") as f:
            json.dump(chunk, f, indent=2)
        # upload chunk to Baserow (table id as needed)
        update_table_rows_batch(collections["id"], chunk)
        sleep(3)

    res_chunks = list(chunk_list(res, 100))
    for idx, chunk in enumerate(res_chunks[:sample], start=1):
        fname = f"chunks/res_chunk_{idx}.json"
        with open(fname, "w") as f:
            json.dump(chunk, f, indent=2)
        update_table_rows_batch(resources["id"], chunk)
        sleep(3)

    print("Data uploaded to Baserow")
