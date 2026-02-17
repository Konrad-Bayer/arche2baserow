import os
import glob
import json
import re

from time import sleep
from tqdm import tqdm
from template import COLLECTION, RESOURCE
from utils.baserow import (create_id_list,
                           create_database_table,
                           update_table_rows_batch,
                           update_table_field_types)
from config import (jwt_token, BASEROW_DB_ID)

konrad_bayer_uri = "https://d-nb.info/gnd/118507753/"


def natural_key(path: str):
    name = os.path.basename(path)
    parts = re.split(r'(\d+)', name)
    # convert digit parts to int, keep non-digits as lower-case strings
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def list_directories_or_files(path: str, data: list | dict) -> list[str]:
    """List all directories or files in a given path."""
    content = sorted(glob.glob(os.path.join(path, "*")),
                     key=natural_key)
    for idx, item in enumerate(tqdm(content, total=len(content))):
        nextItem = content[idx + 1] if idx + 1 < len(content) else None
        nextItemName = os.path.basename(nextItem) if nextItem else None
        name = os.path.basename(item)
        print(f"Processing: {name}")
        name_list = name.split("_")
        is_part_of = os.path.dirname(item).split("/")[-1]
        if is_part_of == "Taschenkalender":
            is_part_of = "kalender"
        if len(name_list) > 1:
            hasNextItem = None
            if os.path.isdir(item):
                name1 = None
                name2 = None
                date = None
                title = None
                author = None
                actor = None
                collection = None
                print(f"Directory: {item}")
                if "_briefe-an" in name or "_briefe-von" in name\
                        or "_briefe-mappen" in name\
                        or "_mappen-zu-briefe" in name:
                    if len(name_list) == 3:
                        identifier = "_".join(name_list[0:3])
                        title = name_list[2]
                    else:
                        identifier = name_list[0]
                        title = name_list[1]
                    collection = "korrespondenz"
                else:
                    firstChildItem = sorted(
                        glob.glob(os.path.join(item, "*")),
                        key=natural_key)[0]\
                        if glob.glob(os.path.join(item, "*")) else None
                    hasNextItem = os.path.basename(firstChildItem)\
                        if firstChildItem else None
                    if "Korrespondenz" in item:
                        identifier = name_list[0]
                        name1 = name_list[1]
                        name2 = name_list[2]
                        if name_list[3].startswith("19"):
                            date = name_list[3]
                        else:
                            title = name_list[3]
                        if len(name_list) > 4:
                            if title:
                                title += "_" + "_".join(name_list[4:])
                            else:
                                title = "_".join(name_list[4:])
                        collection = "korrespondenz"
                    else:
                        identifier = name_list[0]
                        title = name_list[1]
                        date = title.split("-")[1]
                        collection = "kalender"
                if name1 and name2:
                    if "von" in name1:
                        author = name1
                        actor = name2
                    else:
                        author = name2
                        actor = name1
                if author and actor:
                    # if author == "von-bayer-konrad":
                    #     author = konrad_bayer_uri
                    # if actor == "an-bayer" or actor == "an-bayer-konrad":
                    #     actor = konrad_bayer_uri
                    author = " ".join(author.split("-"))
                    actor = " ".join(actor.split("-"))
                data_item = {
                    "name": name,
                    "identifier": identifier,
                    "author": author,
                    "actor": actor,
                    "date": date,
                    "title": title,
                    "isPartOf": is_part_of.lower(),
                    "page": None,
                    "collection": collection,
                    "type": "Collection",
                    "hasNextItem": hasNextItem,
                    "path": item,
                }
                # data_item["children"] = []
                list_directories_or_files(item, data)
            elif os.path.isfile(item):
                print(f"File: {item}")
                hasNextItem = nextItemName
                identifier = f"{name_list[1]}/{name}"
                if "Korrespondenz" in item:
                    collection = "korrespondenz"
                    page = "_".join(name_list[2:]).replace(".tiff", "")
                else:
                    collection = "kalender"
                    page = "_".join(name_list[3:]).replace(".tiff", "")
                data_item = {
                    "name": name,
                    "identifier": identifier,
                    "author": None,
                    "actor": None,
                    "date": None,
                    "title": None,
                    "isPartOf": name_list[1],
                    "page": page,
                    "collection": collection,
                    "type": "Resource",
                    "hasNextItem": hasNextItem,
                    "path": item,
                }
            else:
                continue
            data.append(data_item)
        else:
            # if name == "Taschenkalender":
            #     name = "Kalender"
            # data_item = {
            #     "name": name,
            #     "isPartOf": is_part_of,
            #     "path": item,
            #     "type": "Collection" if os.path.isdir(item) else "Resource"
            # }
            # # data_item["children"] = []
            list_directories_or_files(item, data)
            # data.append(data_item)
    return data


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

        if prop == "hasAuthor" or prop == "hasActor":
            literal = f"{item['author']} - {item['actor']}" if item["author"]\
                and item["actor"] else None
        else:
            literal = ""
        if prop == "hasTemporalCoverage" or prop == "hasCoverageStartDate"\
                or prop == "hasCoverageEndDate":
            date = item["date"] if item["type"] == "Collection" else None
        else:
            date = ""
        print(f"Creating {prop} template...")
        template.append({
            "id": ids,
            "Subject_uri": uri,
            "Class": create_id_list(default_classes, classes_name),
            "Predicate_uri": create_id_list(default_properties, prop),
            "Object_uri_persons": [],
            "Object_uri_places": [],
            "Object_uri_organizations": [],
            "Object_uri_resource": [],
            "Object_uri_vocabs": [],
            "Literal": literal,
            "Language": "de",
            "Date": date,
            "Number": None,
            "Inherit": [],
            "isPartOf": uri_path if prop == "isPartOf" else "",
        })
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

    cols = align_files_with_template(collection_data, COLLECTION, "Collection")
    res = align_files_with_template(resource_data, RESOURCE, "Resource")

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
    # extract_data_from_files()
    create_arche_baserow()
    with open("cols.json", "r") as f:
        cols = json.load(f)
    with open("res.json", "r") as f:
        res = json.load(f)

    os.makedirs("chunks", exist_ok=True)
    cols_chunks = list(chunk_list(cols, 100))
    for idx, chunk in enumerate(cols_chunks, start=1):
        fname = f"chunks/cols_chunk_{idx}.json"
        with open(fname, "w") as f:
            json.dump(chunk, f, indent=2)
        # upload chunk to Baserow (table id as needed)
        update_table_rows_batch("5194", chunk)
        sleep(3)

    res_chunks = list(chunk_list(res, 100))
    for idx, chunk in enumerate(res_chunks, start=1):
        fname = f"chunks/res_chunk_{idx}.json"
        with open(fname, "w") as f:
            json.dump(chunk, f, indent=2)
        update_table_rows_batch("5195", chunk)
        sleep(3)

    print("Data uploaded to Baserow")
