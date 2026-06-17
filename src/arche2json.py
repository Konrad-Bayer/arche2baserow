from utils.arche import (
    get_elements,
    parse_rdf_xml,
    save_dict,
    save_rdf_xml,
    create_baserow_json,
    extend_baserow_json,
    extend_baserow_json2
)
from config import (SCHEMA_PATH, XPATHS)

# Arche xpaths
classes_x = XPATHS["classes"]
properties_x = XPATHS["properties"]
label_x = XPATHS["label"]
comment_x = XPATHS["comment"]

# Arche schema url
url = SCHEMA_PATH

# parse schema create lists of classes and properties
schema = parse_rdf_xml(url)
classes = get_elements(schema, classes_x)
properties = get_elements(schema, properties_x)

# create standard baserow json files of classes, object properties and datatype properties
properties_dict, properties_dict_ids = create_baserow_json(properties, label_x, comment_x)
classes_dict, classes_dict_ids = create_baserow_json(classes, label_x, comment_x)

# save standard baserow json files of classes, object properties and datatype properties
save_rdf_xml(schema, "schema")
save_dict(classes_dict, "classes_default")
save_dict(properties_dict, "properties_default")
save_dict(classes_dict_ids, "classes_ids")
save_dict(properties_dict_ids, "properties_ids")

print("creating properties dict")
# create extended dict for properties
#####################################
properties_dict_ext = extend_baserow_json2(
    properties_dict,
    properties_dict_ids,
    "Subproperties",
    xpath="subPropertyOf",
    xpath2="ObjectProperty",
    schema=schema
)
# extend dict with ids from classes_dict_ids
properties_dict_ext = extend_baserow_json2(
    properties_dict_ext,
    classes_dict_ids,
    "Domain",
    xpath="domain",
    xpath2="ObjectProperty",
    schema=schema
)
properties_dict_ext = extend_baserow_json2(
    properties_dict_ext,
    classes_dict_ids,
    "Range",
    xpath="range",
    xpath2="ObjectProperty",
    schema=schema
)
properties_dict_ext = extend_baserow_json2(
    properties_dict_ext,
    classes_dict_ids,
    "Domain",
    xpath="domain",
    xpath2="DatatypeProperty",
    schema=schema
)
properties_dict_ext = extend_baserow_json2(
    properties_dict_ext,
    classes_dict_ids,
    "Range",
    xpath="range",
    xpath2="DatatypeProperty",
    schema=schema
)
print("classes properties dict")
# create extended dict with ids from classes_dict_ids
#####################################################
classes_dict_ext = extend_baserow_json2(
    classes_dict,
    classes_dict_ids,
    "Subclasses",
    xpath="subClassOf",
    xpath2="Class",
    schema=schema
)
classes_dict_ext = extend_baserow_json(
    classes_dict_ext,
    properties_dict_ids,
    schema=schema
)

save_dict(classes_dict_ext, "classes")
save_dict(properties_dict_ext, "properties")
print("done")
