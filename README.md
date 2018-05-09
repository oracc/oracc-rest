A RESTful API for querying the ORACC database using ElasticSearch.

## Calling the search functionality

The search can be accessed at the `/search` endpoint of a server running
ElasticSearch, e.g.:

```curl -XGET localhost:5000/search' -d 'headword=water'```

This mode supports searching a single field (e.g. headword) for the given value.
If more than one fields are specified (or if none are), an error will be
returned.

A second, more general, search mode is provided at the `/search/<query>`
endpoint. This searches multiple fields for the given query word and returns all
results. The list of fields currently searched is: headword, gw (guideword), cf
(cuniform), senses.mng (meaning), forms.n and norms.n (lemmatisations).

A third endpoint at `/search_all` can be used to retrieve all indexed entries.

In all cases, the result is a JSON array with the full contents of each hit. If
no matches are found, a 204 (No Content) status code is returned.


## Indexing the data

On a machine with elasticsearch installed, start the ElasticSearch service
(e.g. on OS X, type `elasticsearch`; on Ubuntu, `systemctl start elasticsearch`).
This will make an instance of ElasticSearch accessible on port 9200 by default.

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

To enable the search endpoints described above, the Flask server must also be
started. To do this, from the top-level directory do:
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run &
```
This will start the server on port 5000 (by default) and expose the endpoints.
To run the server on a different port, specify (e.g.) `flask run --port 3000`,
and adjust the port number in the curl calls to `localhost/search` etc.
Additionally, this starts the server in development mode, so any changes to the
code should be picked up automatically and make the server restart.
