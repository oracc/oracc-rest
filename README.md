A RESTful API for querying the Oracc database using ElasticSearch.

## Install instructions

This codebase has been written in Python and has been tested in Python 3. To
install all necessary Python modules:

```
pip install -r requirements.txt
```

### Installing jq

We use the [jq](https://stedolan.github.io/jq/) tool to efficiently preprocess
large glossary files. This can be easily installed through a package manager:

-   OS X: `brew install jq`
-   Ubuntu: `sudo apt-get install jq`

You can check that jq has been installed with `jq --version`

For more installation instructions and options, see
[the tool's official page](https://stedolan.github.io/jq/download/).

### ElasticSearch management

To store Oracc's texts and their related metadata, we use
[ElasticSearch](https://www.elastic.co/products/elasticsearch). The code in
this repository has been tested with ElasticSearch 6.
In particular, **it is not (yet) compatible with ElasticSearch 7!**

To install ElasticSearch:

-   OS X: `brew install elasticsearch`
-   Ubuntu: see [this link with instructions](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html).

This API also requires the [ICU Analysis plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html).
To install it:

-   OS X: `elasticsearch-plugin install analysis-icu`
-   Ubuntu: `sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install analysis-icu` (as per link above)

Note that, after installing the plugin, if ElasticSearch was already running then each node has to be restarted.
If running as a service (like in the instructions below), all nodes can be restarted with one command:

-   OS X: `brew services restart elasticsearch`
-   Ubuntu: `sudo service elasticsearch restart`

To launch an instance of ElasticSearch accessible in its default port 9200:

-   OS X: `elasticsearch -d`
-   Ubuntu: `systemctl start elasticsearch`

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

You can verify that the ICU Analysis plugin has been installed by running:

```
curl "localhost:9200/_cat/plugins?v&s=component&h=name,component,version,description"
```

This should show something like:

```
name    component    version description
FRNKdvi analysis-icu 6.0.1   The ICU Analysis plugin integrates Lucene ICU module into elasticsearch, adding ICU relates analysis components.
```

To stop ElasticSearch:

-   OS X: `pkill -f elasticsearch`
-   Ubuntu: `systemctl stop elasticsearch`

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

To start a local version of the app on your development machine, run:

```
flask run --host localhost --port 8000 --debug
```

---

## Calling Oracc's web server search functionality

### Endpoints

The search can be accessed at the `/search` endpoint of a server running
ElasticSearch and the Oracc web server in this repo, e.g.:

```
curl -XGET localhost:5000/search/water
```

This searches multiple fields for the given query word and returns all
results. The list of fields currently searched is: `gw` (guideword),
`cf` (cuneiform), `senses.mng` (meaning), `forms.n` and `norms.n`
(lemmatisations).

The matching is not exact: an entry is considered to match a query word if it
contains any term starting with the query in the relevant fields. For
example, searching for "cat" would return words with either "cat" or "catch" in
their meanings (among others).

The query can also be a phrase of words separated by spaces. In this case, it
will return results matching **all** of the words in the phrase.

A second endpoint at `/search_all` can be used to retrieve all indexed entries.

In both cases, the result is a JSON array with the full contents of each hit. If
no matches are found, a 204 (No Content) status code is returned.

An older, simpler search mode can also be accessed at the `/search` endpoint:

```
curl -XGET localhost:5000/search -d 'gw=water'
```

This mode supports searching a single field (e.g. guideword) for the given value.
If more than one fields are specified (or if none are), an error will be
returned. This does not accept the extra parameters described below, and should
be considered deprecated.

### Customising the search

You can customise the search by optionally specifying additional parameters.
These are:

-   `sort_by`: the field on which to sort (`gw`, `cf` or `icount`)
-   `dir`: the sorting order, ascending (`asc`) or descending (`desc`)
-   `count`: the maximum number of results

For example, if you want to retrieve the 20 entries that appear most frequently
in the indexed corpus, you can request this at:

```
localhost:5000/search_all?sort_by=icount&dir=desc&count=20
```

### Paginating the results

If you don't want to retrieve all results at once, you can use a combination of
the `count` parameter described above and the `after` parameter. The latter
takes a "sorting threshold" and only returns entries whose sorting score is
greater or lesser (for ascending or descending search, respectively) than this
threshold.

### Suggesters

Two other end points can be accessed at the `/suggest` and `/completion` endpoints
of a server running ElasticSearch and the Oracc web server in this repo.
In the case of `/suggest` e.g.:

```
curl -XGET localhost:5000/suggest/yam
```

This searches both `gw` (guideword) and `cf` (cuneiform) fields for words which are
within a distance of 2 changes from the query word, e.g.: `yam` returns `ym` and `ya` (`cf`).

In the case of `/completion` e.g.:

```
curl -XGET localhost:5000/completion/go
```

This searches both `gw` (guideword) and `cf` (cuneiform) fields for words which begin
with the query. This works for single letters or fragments of words.
e.g.: `go` returns `god` and `goddess`

**Important note**: The sorting score depends on the field being sorted on, but
it is _not_ equal to the value of that field! Instead, you can retrieve an
entry's score by looking at the `sort` field returned with each hit. You can
then use this value as the threshold when requesting the next batch of results.

## Running the tests

The code is accompanied by tests written for the [pytest](https://pytest.org)
library (installed with the requirements), which can help ensure that important
functionality is not broken. To run the tests after making changes, execute

```
python -m pytest tests
```

from the top-level directory of the repository.
