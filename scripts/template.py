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
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasDepositor",
    "hasCurator",
    "hasCreator",
    "hasTemporalCoverage",
    "hasSpatialCoverage",
    "hasActor",
    "hasPid",
    "hasFunder",
    "hasPrincipalInvestigator",
    "hasLanguage",
    "hasLifeCycleStatus",
    "hasCoverageStartDate",
    "hasCoverageEndDate",
    "hasCustomCitation"
]
COLLECTION = [
    "hasTitle",
    "hasAuthor",
    "hasActor",
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
    "hasOaiSet",
    "hasCurator",
    "hasContact",
    "hasCustomCitation",
    "hasTemporalCoverage",
    "hasCoverageStartDate",
    "hasCoverageEndDate"
]
RESOURCE = [
    "hasTitle",
    "hasAuthor",
    "hasActor",
    "hasMetadataCreator",
    "hasRelatedDiscipline",
    "hasOwner",
    "hasRightsHolder",
    "hasLicensor",
    "hasDepositor",
    "hasLicense",
    "hasCategory",
    "isPartOf",
    "hasFilename",
    "hasPid",
    "hasFormat",
    "isTitleImageOf",
    "hasCurator",
    "hasCreator",
    "hasAccessRestriction",
    "hasTag",
    "hasCreatedStartDateOriginal",
    "hasCreatedEndDateOriginal",
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
# export object can be extentent with more tables
BASEROW_PROJECT_TABLE = {
    # "Project": PROJECT,
    "TopCollection": TOPCOLLECTION,
    "Collection": COLLECTION,
    "Resource": RESOURCE,
    # "Metadata": METADATA,
    # "Publication": PUBLICATION
}
