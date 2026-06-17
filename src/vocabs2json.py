from utils.arche import (
    get_elements,
    parse_rdf_xml,
    save_dict,
    save_rdf_xml,
    create_baserow_json
)
from config import (VOCABS_PATH)

urls = {
    "vocabs_categories": f"{VOCABS_PATH}ARCHE/arche_resourcetypecategory/archecategory.rdf",
    "vocabs_access_restriction": f"{VOCABS_PATH}ARCHE/arche_accessrestrictions/archeaccessrestrictions.rdf",
    "vocabs_licenses": f"{VOCABS_PATH}ARCHE/arche_licenses/archelicenses.rdf",
    "vocabs_lifecyclestatus": f"{VOCABS_PATH}ARCHE/arche_lifecyclestatus/archelifecyclestatus.rdf",
    "vocabs_oaisets": f"{VOCABS_PATH}ARCHE/arche_oaisets/archeoaisets.rdf",
    "vocabs_oefosdisciplines": f"{VOCABS_PATH}GeneralConcepts/OeFOS/oefos_disciplines.rdf",
    "vocabs_languagecodes": f"{VOCABS_PATH}GeneralConcepts/ISO639_3LanguageCodes/ISO-639-3-languages.rdf"
}
label_x = "./skos:prefLabel[@xml:lang='en']/text()"
comment_x = "./skos:definition[@xml:lang='en']/text()"

for url in urls.values():
    print(url)
    filename = url.split("/")[-1].split(".")[0]

    # parse schema create lists of classes and properties
    schema = parse_rdf_xml(url)
    classes = get_elements(schema, "//rdf:Description")

    # create standard baserow json files of classes, object properties and datatype properties
    classes_dict, classes_dict_ids = create_baserow_json(classes, label_x, comment_x)

    # save standard baserow json files of classes, object properties and datatype properties
    save_rdf_xml(schema, filename)
    save_dict(classes_dict, filename)

print("done")
