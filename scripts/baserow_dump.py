import os
from config import (
    br_client,
    BASEROW_DB_ID,
    MAPPING_PROJECT,
    MAPPING_PERSONS,
    MAPPING_ORGS,
    MAPPING_PLACES,
)
from utils.denormalize import denormalize_json


output_folder = "json_dumps"
os.makedirs(output_folder, exist_ok=True)

if isinstance(BASEROW_DB_ID, str) or isinstance(BASEROW_DB_ID, int) and BASEROW_DB_ID != 0:
    print("Downloading data from Baserow...")
    files = br_client.dump_tables_as_json(BASEROW_DB_ID, folder_name=output_folder, indent=2)
    print("Data downloaded.")

    print("Denormalizing data...")
    denormalize_json("Project", output_folder, MAPPING_PROJECT)
    denormalize_json("Persons", output_folder, MAPPING_PERSONS)
    denormalize_json("Organizations", output_folder, MAPPING_ORGS)
    denormalize_json("Places", output_folder, MAPPING_PLACES)
    print("Data denormalized.")
