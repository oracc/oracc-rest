A RESTful API for querying the ORACC database using ElasticSearch.

## Install instructions
This codebase has been written in Python and has been tested in Python 3. To
install all necessary Python modules:

```
pip install -r requirements.txt
```

### ElasticSearch management
To store ORACC's texts and their related metadata, we use
[ElasticSearch](https://www.elastic.co/products/elasticsearch). The code in
this repository has been tested with ElasticSearch 5 and 6.

To install ElasticSearch:
* OS X: `brew install elasticsearch`
* Ubuntu: see [this link with instructions](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html).

To launch an instance of ElasticSearch accessible in its default port 9200:
* OS X: `elasticsearch -d`
* Ubuntu: `systemctl start elasticsearch`

You can check ElasticSearch was successfully launched by running:

```
curl localhost:9200
```

The output should show something similar to this:

```
{
  "name" : "RAjuGHr",
  "cluster_name" : "elasticsearch_raquel",
  "cluster_uuid" : "QnjkS8UATzCIIAil2HMAYQ",
  "version" : {
    "number" : "6.1.1",
    "build_hash" : "bd92e7f",
    "build_date" : "2017-12-17T20:23:25.338Z",
    "build_snapshot" : false,
    "lucene_version" : "7.1.0",
    "minimum_wire_compatibility_version" : "5.6.0",
    "minimum_index_compatibility_version" : "5.0.0"
  },
  "tagline" : "You Know, for Search"
}
```

To stop ElasticSearch:
* OS X: `pkill -f elasticsearch`
* Ubuntu: `systemctl stop elasticsearch`


## Indexing the data

Before the search can be used, the data must be uploaded to ElasticSearch. This
can be done with `python -m ingest.bulk_upload`, which will ingest the glossary
files located in the [neo](neo) folder. The [ingest](ingest) folder has
some additional information and alternative ways of performing the indexing.
More documentation will be added about this in due course.

**NB**: At the moment, ingesting the data first deletes any previous version
of it that may exist on the ElasticSearch instance, rather than updating it!

Once the data is indexed, it can be queried with ElasticSearch directly (either
through an API or from the command line, by sending HTTP requests with `curl`).


## Setting up the server

To enable the search endpoints described below, the Flask server must also be
started. To do this, from the top-level directory do:
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run &
```
This will start the server on port 5000 (by default) and expose the endpoints.
To run the server on a different port, specify (e.g.) `flask run --port 3000`,
and adjust the port number in the curl calls to `localhost/search` etc (see below).
Additionally, this starts the server in development mode, so any changes to the
code should be picked up automatically and make the server restart.

## Calling ORACC's web server search functionality

The search can be accessed at the `/search` endpoint of a server running
ElasticSearch and the ORACC web server in this repo, e.g.:

```
curl -XGET localhost:5000/search -d 'headword=water'
```

This mode supports searching a single field (e.g. headword) for the given value.
If more than one fields are specified (or if none are), an error will be
returned.

A second, more general, search mode is provided at the `/search/<query>`
endpoint. For example:

```
curl -XGET localhost:5000/search/water
```

This searches multiple fields for the given query word and returns all
results. The list of fields currently searched is: `headword`, `gw`
(guideword), `cf` (cuneiform), `senses.mng` (meaning), `forms.n` and `norms.n`
(lemmatisations).

A third endpoint at `/search_all` can be used to retrieve all indexed entries.

In all cases, the result is a JSON array with the full contents of each hit. If
no matches are found, a 204 (No Content) status code is returned.


## Running the tests
The code is accompanied by tests written for the [pytest](https://pytest.org)
library (installed with the requirements), which can help ensure that important
functionality is not broken. To run the tests after making changes, execute
```
python -m pytest tests
```
from the top-level directory of the repository.
