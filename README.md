# ARCHE Constants Metadata Creator

This Repository is used to create Baserow tables for creating ARCHE Metadata.
It creates the following tables:

* Classes (All available vocabs:ARCHE classes like: Project, TopCollection, Collection, etc.)
* Properties (All available vocabs:ARCHE properties like: hasTitle, hasDescription, etc.)
* Vocabs (All available vocabularies from [vocabs.acdh.oeaw.ac.at](https://vocabs.acdh.oeaw.ac.at).)
* Project (A table linked to all other tables for creating ARCHE constants project metadata.)
* Persons (A table for creating ARCHE constants person metadata.)
* Organizations (A table for creating ARCHE constants organization metadata.)
* Places (A table for creating ARCHE constants places metadata.)

## Usage (Github Actions)

### Setup Baserow (Github Actions)

* Login to Baserow and create a new workspace for a project. In this workspace, create a new database and note the database ID.
* Then [create a new API token in Baserow](https://baserow.io/user-docs/personal-api-tokens). 
* Fork this repository and add the API token to the [secrets of the Github repository](https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-development-environment-secrets-for-your-repository-or-organization) as `BASEROW_TOKEN`.
* Add more secrets for the user as `BASEROW_USER` and password as `BASEROW_PW`.  
* [Trigger the workflow manually](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow). This will require the input of the Baserow Database ID you want to use.

### Baserow Data Dump and Turtle (ttl) Serialization (Github Actions)

* Requires the same Github secrets as above.
* [Trigger the workflow manually](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow). This will require the input of the Baserow Database ID you want to use and the ARCHE project Name = TopCollection name in format `my-project-identifier`.

## Installation and Usage (Local)

## Setup Baserow (Local)

Make sure enviroment variables are set for Baserow (see `.secret.example`):

* `BASEROW_USER` (Baserow username)
* `BASEROW_PW` (Baserow password)
* `BASEROW_TOKEN` (Baserow API token)
* `BASEROW_DB_ID` (Baserow Database ID)

Then run the following commands:

```bash
python -m venv venv # create a virtual environment
source venv/bin/activate # activate the virtual environment

pip install -r requirements.txt # install python dependencies

python scripts/arche2json.py # create json files from ARCHE Schema
python scripts/vocabs2json.py # create json files from vocabs.acdh.oeaw.ac.at
python scripts/arche2baserow.py # upload json files to baserow to create tables
```

### Baserow Data Dump and Turtle (ttl) Serialization (Local)

* Requires the same environment variables as above.
* Additional environment variable: `PROJECT_NAME` (ARCHE project Name = TopCollection name in format `my-project-identifier`)

Then run the following commands:

```bash
python -m venv venv # create a virtual environment
source venv/bin/activate # activate the virtual environment

pip install -r requirements.txt # install python dependencies

python scripts/baserow_dump.py # fetch data from baserow and denormalized it
python scripts/arche_constants.py # create ttl file from denormalized data
```

## Output Data Structure

── RDF<br>
   └── arche_constants.ttl<br>

## Useful Links

* [Baserow API](https://baserow.io/user-docs/database-api)
* [Vocabs](https://vocabs.acdh.oeaw.ac.at/)
* [ARCHE](https://arche.acdh.oeaw.ac.at/)
* [ARCHE Schema](https://github.com/acdh-oeaw/arche-schema)
* [ARCHE Metadata Crawler](https://github.com/acdh-oeaw/arche-metadata-crawler)
* [ARCHE Schema Table](https://arche-dev.acdh-dev.oeaw.ac.at/browser/api/getRootTable/de?_format=application/json)