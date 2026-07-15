import json
import re
import glob
import os
from config import PROJECT_NAME, LANG_SPECIAL_TOKEN
from tqdm import tqdm
from acdh_graph_pyutils.graph import (
    create_empty_graph,
    create_custom_triple,
    create_type_triple,
    create_memory_store,
    serialize_graph
)
from acdh_graph_pyutils.namespaces import NAMESPACES
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF

# define namespaces
NAMESPACES["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
NAMESPACES["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
NAMESPACES["xsd"] = "http://www.w3.org/2001/XMLSchema#"
NAMESPACES["arche"] = "https://vocabs.acdh.oeaw.ac.at/schema#"
arche_id = URIRef("https://id.acdh.oeaw.ac.at/")
ARCHE = Namespace(NAMESPACES["arche"])
COLLECTION_NAME = PROJECT_NAME
# create empty graph
G = create_empty_graph(
    namespaces=NAMESPACES,
    identifier=arche_id,
    store=create_memory_store()
)


def create_entity_uri_from_string(string: str) -> URIRef:
    """
    Create an URIRef from a string.
    """
    if isinstance(string, str) and len(string) > 0:
        if ", " in string:
            string = string.split(", ")
            last_name = [re.sub(r"[^a-zA-Z0-9]+", "", string[0])]
            if len(string[1].split(" ")) == 1:
                first_name = re.sub(r"[^a-zA-Z0-9]+", "", string[1].split(" ")[0])
                first_name_letter = first_name[1]
                last_name.insert(0, first_name_letter)
            elif len(string[1].split(" ")) > 1:
                for x in string[1].split(" "):
                    name = re.sub(r"[^a-zA-Z0-9]+", "", x)
                    last_name.insert(0, name[0])
            return URIRef(f'{arche_id}{"".join(last_name).lower()}')
        else:
            return URIRef(f'{arche_id}{string}')
    else:
        return ""


def create_minimal_entity_triple(entity: list, entity_type: str) -> None:
    """
    Create URIRef from string and entity type triple.
    """
    try:
        data = entity["data"]
    except KeyError:
        return
    subject_uri = URIRef(data["Subject_uri"])
    if entity_type == "persons":
        object_uri = URIRef(ARCHE["Person"])
    elif entity_type == "places":
        object_uri = URIRef(ARCHE["Place"])
    elif entity_type == "organizations":
        object_uri = URIRef(ARCHE["Organisation"])
    else:
        raise UnboundLocalError(f"Entity type not defined. {entity_type}")
    create_type_triple(G, subject_uri, object_uri)


def get_entity_uri(
    subject_uri: URIRef,
    predicate_uri: URIRef,
    entity: list,
    entity_type: str = None
) -> None:
    """
    Create an URIRef from a string.
    """
    if isinstance(entity, list) and len(entity) > 0:
        for ent in entity:
            if len(ent["data"]["Subject_uri"]) > 0:
                object_uri = URIRef(ent["data"]["Subject_uri"])
            else:
                continue
            create_custom_triple(G, subject_uri, predicate_uri, object_uri)
            if entity_type is not None:
                create_minimal_entity_triple(ent, entity_type)


def get_resource_uri(
    subject_uri: URIRef,
    predicate_uri: URIRef,
    resource: list,
) -> None:
    """
    Create an URIRef from a string.
    """
    if isinstance(resource, list) and len(resource) > 0:
        for res in resource:
            try:
                object_uri = URIRef(f'{res["data"]["Namespace"]}{res["value"]}')
            except KeyError:
                object_uri = URIRef(f'{arche_id}{res["value"]}')
            create_custom_triple(G, subject_uri, predicate_uri, object_uri)


def get_literal(
    subject_uri: URIRef,
    predicate_uri: URIRef,
    literal: str,
    literal_lang: str
) -> None:
    """
    Create a Literal with or without language from a string.
    """
    if isinstance(literal, str) and len(literal) > 0:
        if isinstance(literal_lang, str) and len(literal_lang) > 0:
            if literal_lang != LANG_SPECIAL_TOKEN:
                create_custom_triple(G, subject_uri, predicate_uri, Literal(literal, lang=literal_lang))
            else:
                create_custom_triple(G, subject_uri, predicate_uri, Literal(literal))
        else:
            if "/" in literal:
                create_custom_triple(G, subject_uri, predicate_uri, URIRef(f'{arche_id}{literal.replace(" ", "")}'))  # fix extra whitespaces in files.py


def get_date(
    subject_uri: URIRef,
    predicate_uri: URIRef,
    date: str
) -> None:
    """
    Create a Literal with datatype date from a string.
    """
    if isinstance(date, str) and len(date) > 0:
        create_custom_triple(G, subject_uri, predicate_uri, Literal(date, datatype=f'{NAMESPACES["xsd"]}date'))


def get_number(
    subject_uri: URIRef,
    predicate_uri: URIRef,
    number: int
) -> None:
    """
    Create a Literal with datatype integer from a string.
    """
    if isinstance(number, int) and len(number) > 0:
        create_custom_triple(G, subject_uri, predicate_uri, Literal(number, datatype=f'{NAMESPACES["xsd"]}integer'))


def create_arche_constants_triples(metadata: dict) -> None:
    """
    Create triples for ARCHE constants from the metadata json file.
    """
    for meta in tqdm(metadata.values(), total=len(metadata)):
        subject_string = meta["Subject_uri"]
        subject_uri = URIRef(f'{arche_id}{subject_string}')
        if isinstance(meta["Class"], list) and len(meta["Class"]) == 1:
            type_class = meta["Class"][0]
            type_uri = URIRef(f'{type_class["data"]["Namespace"]}{type_class["value"]}')
            create_type_triple(G, subject_uri, type_uri)
        if isinstance(meta["Predicate_uri"], list) and len(meta["Predicate_uri"]) == 1:
            predicate_class = meta["Predicate_uri"][0]
            predicate_uri = URIRef(f'{predicate_class["data"]["Namespace"]}{predicate_class["value"]}')
            # create triples from persons
            persons_list = meta["Object_uri_persons"]
            get_entity_uri(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                entity=persons_list,
                entity_type="persons"
            )
            # create triples from places
            places_list = meta["Object_uri_places"]
            get_entity_uri(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                entity=places_list,
                entity_type="places"
            )
            # create triples from organizations
            organizations_list = meta["Object_uri_organizations"]
            get_entity_uri(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                entity=organizations_list,
                entity_type="organizations"
            )
            # create triples from resources
            resource_list = meta["Object_uri_resource"]
            get_resource_uri(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                resource=resource_list
            )
            # create triples from vocabs
            vocabs_list = meta["Object_uri_vocabs"]
            get_resource_uri(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                resource=vocabs_list
            )
            # create triples from literal
            literal = meta["Literal"]
            language = meta["Language"]
            get_literal(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                literal=literal,
                literal_lang=language
            )
            # create triples from date
            date = meta["Date"]
            get_date(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                date=date
            )
            # create triples from number
            number = meta["Number"]
            get_number(
                subject_uri=subject_uri,
                predicate_uri=predicate_uri,
                number=number
            )


def create_arche_entity_triples(file: str) -> None:
    # create graph for ARCHE entities
    # open json file
    files = [
        "Persons_denormalized",
        "Places_denormalized",
        "Organizations_denormalized"
    ]
    fn = file.split("/")[-1].split(".")[0]
    if fn in files:
        with open(file, "r") as f:
            data = json.load(f)
        for meta in tqdm(data.values(), total=len(data)):
            subject_uri = URIRef(meta["Subject_uri"])
            if isinstance(meta["Predicate_uri"], list) and len(meta["Predicate_uri"]) == 1:
                predicate_class = meta["Predicate_uri"][0]
                predicate_uri = URIRef(
                    f'{predicate_class["data"]["Namespace"]}{predicate_class["value"]}')
                # entity_type = fn.replace("_denormalized", "").lower()
                try:
                    get_entity_uri(
                        subject_uri=subject_uri,
                        predicate_uri=predicate_uri,
                        entity=meta["Object_uri_organizations"],
                        entity_type="organizations"
                    )
                except KeyError:
                    # placeholder
                    print("No organizations.")
                get_literal(
                    subject_uri=subject_uri,
                    predicate_uri=predicate_uri,
                    literal=meta["Literal"],
                    literal_lang=meta["Language"]
                )


def inherit_rights_from_parent_collection() -> None:
    """
    Let specific resources inherit rights-related triples from their parent collection.
    """
    resource_type = URIRef(f'{NAMESPACES["arche"]}Resource')
    is_part_of = URIRef(f'{NAMESPACES["arche"]}isPartOf')
    inherited_predicates = [
        URIRef(f'{NAMESPACES["arche"]}hasRightsHolder'),
        URIRef(f'{NAMESPACES["arche"]}hasLicensor'),
        URIRef(f'{NAMESPACES["arche"]}hasOwner')
    ]
    target_subject_fragment = "konradbayer/korrespondenz"

    for subject_uri in G.subjects(RDF.type, resource_type):
        if target_subject_fragment not in str(subject_uri):
            continue
        parent_collection_uri = G.value(subject_uri, is_part_of)
        if not isinstance(parent_collection_uri, URIRef):
            continue
        for predicate_uri in inherited_predicates:
            for object_uri in G.objects(parent_collection_uri, predicate_uri):
                create_custom_triple(G, subject_uri, predicate_uri, object_uri)


# load metadata json files
with open("json_dumps/Project_denormalized.json", "r") as f:
    metadata = json.load(f)
# load metadata json files
with open("json_dumps/Collections_denormalized.json", "r") as f:
    collections = json.load(f)
# load metadata json files
with open("json_dumps/Resources_denormalized.json", "r") as f:
    resources = json.load(f)

# serialize graph
os.makedirs("rdf", exist_ok=True)
ALL_CONSTANTS = [
    metadata,
    collections,
    resources
]
# constant triples
for constant in ALL_CONSTANTS:
    create_arche_constants_triples(constant)
# entities triples
file_glob = glob.glob("json_dumps/*.json")
for file in file_glob:
    create_arche_entity_triples(file)

inherit_rights_from_parent_collection()

serialize_graph(G, "turtle", "rdf/test-arche_constants.ttl")
print("Done with ARCHE constants. file: rdf/test-arche_constants.ttl")
