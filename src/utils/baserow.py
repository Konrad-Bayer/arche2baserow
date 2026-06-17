import requests
from config import (BASEROW_URL, BASEROW_TOKEN)
from tqdm import tqdm


def update_table_rows(br_table_id: int, table: dict) -> None:
    """Updating a Baserow table with a dictionary of rows.
    Baserow table id and dictionary of rows are required."""
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/"
    for x in tqdm(table, total=len(table)):
        row_id = x["id"]
        try:
            url = f"{br_rows_url}{row_id}/?user_field_names=true"
            print("Updating row... \n", url)
            r = requests.patch(
                url,
                headers={
                    "Authorization": f"Token {BASEROW_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=x
            )
            if r.status_code == 200:
                print(f"Updated {row_id}")
            else:
                print(f"Error {r.status_code} with {row_id}")
                print("Row does not exist. Creating...")
                url = f"{br_rows_url}?user_field_names=true"
                print(url)
                r = requests.post(
                    url,
                    headers={
                        "Authorization": f"Token {BASEROW_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=x
                )
                if r.status_code == 200:
                    print(f"Created {row_id}")
                else:
                    print(f"Error {r.status_code} with {row_id}")
        except Exception as e:
            print(f"{e} with {row_id}")


def update_table_rows_batch(br_table_id: int, table: list[dict]) -> None:
    """Batch updating a Baserow table with a dictionary of rows.
    Baserow table id and dictionary of rows are required."""
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/batch/"
    items = {
        "items": table
    }
    # print(items)
    try:
        url = f"{br_rows_url}?user_field_names=true"
        print("Updating row... \n", url)
        r = requests.post(
            url,
            headers={
                "Authorization": f"Token {BASEROW_TOKEN}",
                "Content-Type": "application/json"
            },
            json=items
        )
        print(r.status_code)
        if r.status_code == 200:
            print(f"Updated... Length rows: {len(table)}")
        else:
            print(f"Error {r.status_code}")
            print("Row does not exist. Creating...")
            print(url)
            try:
                r = requests.patch(
                    url,
                    headers={
                        "Authorization": f"Token {BASEROW_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=items
                )
                if r.status_code == 200:
                    print("Created")
                else:
                    print(f"Error {r.status_code}")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


def create_database_table(
    database_id: int,
    token: str,
    table_name: str,
    table_values: list = "Name"
) -> None:
    """Creating a new Baserow table. Baserow database id, JWT token and table name are required."""
    br_db_url = f"{BASEROW_URL}database/tables/database/{database_id}/"
    table = {
        "name": table_name
    }
    if isinstance(table_values, list):
        table["first_row_header"] = True
        table["data"] = []
        for x in table_values:
            x.pop("id")
            x.pop("order")
        table["data"].append([k for k in table_values[0].keys()])
        for x in table_values:
            table["data"].append([v for v in x.values()])
    else:
        table["first_row_header"] = True
        table["data"] = [[table_values]]
    print("Creating table... ", table_name, " ", br_db_url)
    r = requests.post(
        br_db_url,
        headers={
            "Authorization": f"JWT {token}",
            "Content-Type": "application/json"
        },
        json=table
    )
    if r.status_code == 200:
        response = r.json()
        print("Table created... ", response["id"])
        return response
    else:
        print(f"Error {r.status_code} with {database_id}")
        return r.json()


def update_table_field_types(
    table_id: int,
    token: str,
    default_fields: dict
) -> None:
    """Upading Baserow table field types. Baserow table id, JWT token, default fields and"""
    br_table_url = f"{BASEROW_URL}database/fields/table/{table_id}/"
    for x in tqdm(default_fields, total=len(default_fields)):
        print("Updating table field types... ", br_table_url)
        r = requests.patch(
            br_table_url,
            headers={
                "Authorization": f"JWT {token}",
                "Content-Type": "application/json"
            },
            json=x
        )
        if r.status_code == 200:
            print(f"Updated field {x['name']} in {table_id}")
        else:
            url = f"{br_table_url}?user_field_names=true"
            print(f"Error {r.status_code} with {table_id}")
            print("Field does not exist. Creating...")
            r = requests.post(
                url,
                headers={
                    "Authorization": f"JWT {token}",
                    "Content-Type": "application/json"
                },
                json=x
            )
            if r.status_code == 200:
                print(f"Created field {x['name']} in {table_id}")
            else:
                print(f"Error {r.status_code} with {table_id}")


def delete_table_field(
    table_id: int,
    token: str,
    field_names: list = ["Notes", "Active"]
) -> None:
    """Delete table fields of a Baserow table. Baserow table id, JWT token and field ids are required."""
    br_table_url = f"{BASEROW_URL}database/fields/table/{table_id}/"
    r = requests.get(
        br_table_url,
        headers={
            "Authorization": f"JWT {token}",
            "Content-Type": "application/json"
        },
    )
    if r.status_code == 200:
        response = r.json()
        for x in response:
            if x["name"] in field_names:
                print("Deleting field... ", x["id"])
                url = f"{BASEROW_URL}database/fields/{x['id']}/"
                r = requests.delete(
                    url,
                    headers={
                        "Authorization": f"JWT {token}",
                        "Content-Type": "application/json"
                    },
                )
                if r.status_code == 200:
                    print(f"Deleted field {x['id']} in {table_id}")
                else:
                    print(f"Error {r.status_code} with {table_id}")
        return response
    else:
        print(f"Error {r.status_code} with {table_id}")
        return r.json()


def get_properties(template: dict[str, list[str]], class_name: str):
    return template[class_name]


def create_id_list(list: list[dict], name: str):
    domain = "https://vocabs.acdh.oeaw.ac.at/schema#"
    return [x["id"] for x in list if x["Name"] == name and x["Namespace"] == domain]


def create_template_lists(ids: int,
                          custom_properties: list[str],
                          classes_name: str,
                          default_properties: list[dict],
                          default_classes: list[dict]):
    template = []
    for prop in custom_properties:
        print(f"Creating {prop} template...")
        template.append({
            "id": ids,
            "order": f"{ids}.00000000000000000000",
            "Subject_uri": classes_name.split("_")[1],
            "Class": create_id_list(default_classes, classes_name.split("_")[0]),
            "Predicate_uri": create_id_list(default_properties, prop),
            "Object_uri_persons": [],
            "Object_uri_places": [],
            "Object_uri_organizations": [],
            "Object_uri_resource": [],
            "Object_uri_vocabs": [],
            "Literal": "",
            "Language": "",
            "Date": None,
            "Number": None,
            "Inherit": []
        })
        ids += 1
    return ids, template
