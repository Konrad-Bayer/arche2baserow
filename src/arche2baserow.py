import json
# import os
from time import sleep
from config import (jwt_token, BASEROW_DB_ID)
from template import BASEROW_PROJECT_TABLE
from utils.baserow import (create_database_table,
                           update_table_field_types,
                           update_table_rows_batch,
                           delete_table_field,
                           create_template_lists,
                           get_properties)

vocabs_files = {
    "vocabs_categories": "out/archecategory.json",
    "vocabs_access_restriction": "out/archeaccessrestrictions.json",
    "vocabs_licenses": "out/archelicenses.json",
    "vocabs_lifecyclestatus": "out/archelifecyclestatus.json",
    "vocabs_oaisets": "out/archeoaisets.json",
    "vocabs_oefosdisciplines": "out/oefos_disciplines.json",
    "vocabs_languagecodes": "out/ISO-639-3-languages.json"
}

merged_table = []
for file in vocabs_files.values():
    filename = file.split("/")[-1].split(".")[0]
    # load json files with classes
    with open(file, "r") as f:
        table = json.load(f)
    merged_table.extend(table)

with open("out/Vocabs.json", "w") as f:
    json.dump(merged_table, f, indent=2)

# create table
vocabs = create_database_table(
    BASEROW_DB_ID, jwt_token, "Vocabs", merged_table)
print("Vocabs uploaded to Baserow...")
sleep(1)

# load json files with classes and properites
with open("out/properties_default.json", "r") as f:
    properties_table = json.load(f)
with open("out/classes_default.json", "r") as f:
    classes_table = json.load(f)

# create tables
classes = create_database_table(
    BASEROW_DB_ID, jwt_token, "Classes", classes_table)
sleep(1)
properties = create_database_table(
    BASEROW_DB_ID, jwt_token, "Properties", properties_table)
sleep(1)
persons = create_database_table(
    BASEROW_DB_ID, jwt_token, "Persons")
sleep(1)
places = create_database_table(
    BASEROW_DB_ID, jwt_token, "Places")
sleep(1)
organizations = create_database_table(
    BASEROW_DB_ID,
    jwt_token,
    "Organizations"
)
sleep(1)
project = create_database_table(
    BASEROW_DB_ID,
    jwt_token,
    "Project",
    "Subject_uri"
)
sleep(1)
print(classes)
print(properties)
print(persons)
print(places)
print(organizations)
print(project)
print("Tables created...")

try:
    class_table = classes["id"]
    properties_table = properties["id"]
except KeyError:
    print("KeyError: tables not found")
    exit()

print("Updating table fields...")

# class table fields
default_fields = [
    {"name": "Notes", "type": "long_text"},
    {"name": "Namespace", "type": "text"},
    {"name": "Label", "type": "text"},
    {
        "name": "Subclasses",
        "type": "link_row",
        "link_row_table_id": classes["id"],
        "has_related_field": False
    },
    {"name": "Subclasses_NonLinked", "type": "text"},
    {
        "name": "Max1",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {
        "name": "Min1",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    }
]
classes_fields = update_table_field_types(
    class_table,
    jwt_token,
    default_fields
)
sleep(1)

# properties table fields
default_fields = [
    {"name": "Notes", "type": "long_text"},
    {"name": "Namespace", "type": "text"},
    {"name": "Label", "type": "text"},
    {
        "name": "Subproperties",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {"name": "Subproperties_NonLinked", "type": "text"},
    {
        "name": "Domain",
        "type": "link_row",
        "link_row_table_id": classes["id"],
        "has_related_field": False
    },
    {"name": "Domain_NonLinked", "type": "text"},
    {
        "name": "Range",
        "type": "link_row",
        "link_row_table_id": classes["id"],
        "has_related_field": False
    },
    {"name": "Range_NonLinked", "type": "text"},
]
properties_fields = update_table_field_types(
    properties_table,
    jwt_token,
    default_fields
)
sleep(1)

# persons table fields
default_fields = [
    {"name": "Name", "type": "text"},
    {"name": "Subject_uri", "type": "text"},
    {
        "name": "Predicate_uri",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {"name": "Literal", "type": "text"},
    {
        "name": "Object_uri_organizations",
        "type": "link_row",
        "link_row_table_id": organizations["id"],
        "has_related_field": False
    },
    {"name": "Language", "type": "text"}
]
persons_fields = update_table_field_types(
    persons["id"],
    jwt_token,
    default_fields
)
sleep(1)
delete_table_field(persons["id"], jwt_token, ["Notes", "Active"])
sleep(1)

# places table fields
default_fields = [
    {"name": "Name", "type": "text"},
    {"name": "Subject_uri", "type": "text"},
    {
        "name": "Predicate_uri",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {"name": "Literal", "type": "text"},
    {"name": "Language", "type": "text"}
]
places_fields = update_table_field_types(
    places["id"],
    jwt_token,
    default_fields
)
sleep(1)
delete_table_field(places["id"], jwt_token, ["Notes", "Active"])
sleep(1)

# organizations table fields
default_fields = [
    {"name": "Name", "type": "text"},
    {"name": "Subject_uri", "type": "text"},
    {
        "name": "Predicate_uri",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {"name": "Literal", "type": "text"},
    {"name": "Language", "type": "text"}
]
organizations_fields = update_table_field_types(
    organizations["id"],
    jwt_token,
    default_fields
)
sleep(1)
delete_table_field(organizations["id"], jwt_token, ["Notes", "Active"])
sleep(1)

# project table fields
default_fields = [
    {"name": "Subject_uri", "type": "text"},
    {
        "name": "Class",
        "type": "link_row",
        "link_row_table_id": classes["id"],
        "has_related_field": False
    },
    {
        "name": "Predicate_uri",
        "type": "link_row",
        "link_row_table_id": properties["id"],
        "has_related_field": False
    },
    {
        "name": "Object_uri_persons",
        "type": "link_row",
        "link_row_table_id": persons["id"],
        "has_related_field": False
    },
    {
        "name": "Object_uri_places",
        "type": "link_row",
        "link_row_table_id": places["id"],
        "has_related_field": False
    },
    {
        "name": "Object_uri_organizations",
        "type": "link_row",
        "link_row_table_id": organizations["id"],
        "has_related_field": False
    },
    {
        "name": "Object_uri_resource",
        "type": "link_row",
        "link_row_table_id": project["id"],
        "has_related_field": False
    },
    {
        "name": "Object_uri_vocabs",
        "type": "link_row",
        "link_row_table_id": vocabs["id"],
        "has_related_field": False
    },
    {"name": "Literal", "type": "text"},
    {"name": "Language", "type": "text"},
    {"name": "Date", "type": "text"},
    {"name": "Number", "type": "number"},
    {
        "name": "Inherit",
        "type": "link_row",
        "link_row_table_id": classes["id"],
        "has_related_field": False
    }
]
project_fields = update_table_field_types(
    project["id"],
    jwt_token,
    default_fields
)
# sleep(1)
# delete_table_field(project["id"], jwt_token, ["Notes", "Active"])
sleep(1)

# Upading Baserow table rows
with open("out/properties.json", "r") as f:
    properties: list[dict] = json.load(f)
with open("out/classes.json", "r") as f:
    classes: list[dict] = json.load(f)

update_table_rows_batch(properties_table, properties)
sleep(3)
update_table_rows_batch(class_table, classes)
sleep(3)

# create template lists
ids = 1
for key, value in BASEROW_PROJECT_TABLE.items():
    print(f"Updating {key} table rows...")
    ids_update, custom_template_project = create_template_lists(
        ids,
        value,
        key,
        properties,
        classes,
    )
    ids = ids_update
    with open(f"out/{key}.json", "w") as f:
        json.dump(custom_template_project, f, indent=2)
    update_table_rows_batch(project["id"],
                            custom_template_project)
    sleep(3)
print("Done...")
print("Data uploaded to Baserow")
