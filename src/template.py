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
    "hasTemporalCoverage",
    "hasSpatialCoverage",
    "hasRightsHolder",
    "hasOwner",
    "hasLicensor",
    "hasEditor",
    "hasDepositor",
    "hasCurator",
    "hasCoverageEndDate",
    "hasCoverageStartDate",
    "hasActor"
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
    "hasDepositor",
    "hasCreator",
    "isPartOf",
    "hasPid",
    "hasLanguage",
    "hasSubject",
    "hasCurator",
    "hasTemporalCoverage",
    "hasCoverageStartDate",
    "hasCoverageEndDate",
    "hasDigitisingAgent",
    "hasContact"
]
COLLECTION_SUB = [
    "hasTitle",
    "hasCreator",
    "hasActor",
    "hasMetadataCreator",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "isPartOf",
    "hasPid",
    "hasSubject",
    "hasOaiSet",
    "hasSpatialCoverage",
    "hasCoverageStartDate",
    "hasCoverageEndDate",
    "hasTag",
    "hasNextItem",
    "hasLanguage",
    "hasCurator",
    "hasRelatedDiscipline",
    "hasDigitisingAgent",
    "hasDepositor",
    "hasContact"
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
    "hasAuthor",
    "hasActor",
    "hasMetadataCreator",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasLicense",
    "hasAccessRestriction",
    "hasNextItem",
    "hasTag",
    "hasDigitisingAgent",
    "hasCreatedStartDateOriginal",
    "hasCreatedEndDateOriginal",
    "hasSpatialCoverage",
    "hasCategory",
    "hasLanguage",
    "hasRelatedDiscipline",
    "hasOaiSet",
    "hasDepositor",
    "hasCurator",
    "hasContact"
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
    "Collection_correspondence": COLLECTION,
    "Collection_calendar": COLLECTION,
    "Resource": RESOURCE,
    # "Metadata": METADATA,
    # "Publication": PUBLICATION
}
