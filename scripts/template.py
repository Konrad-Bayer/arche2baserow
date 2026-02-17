# Baserow Project table template
PROJECT = [
    "hasTitle",
    "hasDescription",
    "hasContact",
    "hasMetadataCreator",
    "hasRelatedDiscipline",
    "hasSubject",
    "hasRelatedCollection"
]
TOPCOLLECTION = [
    "hasTitle",
    "hasDescription",
    "hasContact",
    "hasMetadataCreator",
    "hasRelatedDiscipline",
    "hasSubject",
    "hasPid",
    "hasFunder",
    "hasPrincipalInvestigator",
    "hasLanguage",
    "hasLifeCycleStatus",
    "hasCustomCitation"
]
COLLECTION = [
    "hasTitle",
    "hasDescription",
    "hasCreator",
    "hasMetadataCreator",
    "hasRelatedDiscipline",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasLicense",
    "hasDepositor",
    "hasCreator",
    "isPartOf",
    "hasPid",
    "hasLanguage",
    "hasSubject",
    "hasCurator",
    "hasCustomCitation",
    "hasTemporalCoverage",
    "hasCoverageStartDate",
    "hasCoverageEndDate",
]
COLLECTION_SUB = [
    "hasTitle",
    "hasAlternativeTitle",
    "hasCreator",
    "hasAuthor",
    "hasActor",
    "isPartOf",
    "hasPid",
    "hasSubject",
    "hasOaiSet",
    "hasTemporalCoverage",
    "hasCoverageStartDate",
    "hasCoverageEndDate",
    "hasTag",
]
RESOURCE = [
    "hasTitle",
    "hasMetadataCreator",
    "hasRelatedDiscipline",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasDepositor",
    "hasLicense",
    "isPartOf",
    "hasFilename",
    "hasPid",
    "hasFormat",
    "hasCurator",
    "hasCreator",
    "hasAccessRestriction",
    "isTitleImageOf",
    "hasCategory",
]
RESOURCE_SUB = [
    "hasTitle",
    "isPartOf",
    "hasFilename",
    "hasPid",
    "hasFormat",
    "hasAccessRestriction",
    "hasNextItem",
    "hasTag",
    "hasCreatedStartDateOriginal",
    "hasCreatedEndDateOriginal",
    "hasCategory",
]
METADATA = [
    "hasTitle",
    "hasMetadataCreator",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasDepositor",
    "hasLicense",
    "hasCategory"
]
PUBLICATION = [
    "hasTitle"
]
PERSON = [
    "hasFirstName",
    "hasLastName",
    "hasPersonalTitle",
]
ORGANIZATION = [
    "hasName",
    "hasAlternativeName",
    "hasAffiliation",
    "hasEmail",
    "hasOrcid",
    "hasGndId"
]
# export object can be extentent with more tables
BASEROW_PROJECT_TABLE = {
    # "Project": PROJECT,
    "TopCollection": TOPCOLLECTION,
    "Collection": COLLECTION,
    "Resource": RESOURCE,
    # "Metadata": METADATA,
    # "Publication": PUBLICATION
}
