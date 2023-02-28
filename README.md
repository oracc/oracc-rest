A Flask RESTful API for querying the Oracc database using Elasticsearch.

The accompanying frontend project for accessing this backend is held in [this](https://github.com/oracc/oracc-search-front-end) repo.

This codebase has been written in Python and has been tested in Python 3.

Before contributing code, you should start by setting up your correct environment for either development or production, see instructions below.

---

## Setting up a development and production environment

For both development and production it is recommended to set up this application using a python virtual environment using an enviornment manager of your choice.

## Development environment

While you can run this application directly on your local machine, you may wish to set up a virtual Ubuntu environment for testing the application locally. This is preferable as it mimics the production environment more closely (see below). You can easily spin up a local virtual Ubuntu environment using [Multipass](https://multipass.run/).

To start, clone the repo to your local machine or virtual Ubuntu environment (you will need Git and Python installed).

### Install python modules

Run the following command from the top-level directory of this repo:

```
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

## Running the Flask API

To enable the search endpoints described below, the Flask server must be started. To do this, from the top-level directory do:

```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run &
```

This will start a dev server on port 5000 (by default) and expose the endpoints. To run the server on a different port, specify (e.g.) `flask run --port 3000`, and adjust the port number in the curl calls to `localhost/search` etc (see below). Additionally, this starts the server in development mode, so any changes to the code should be picked up automatically and make the server restart.

## Production environment

The application is currently deployed for production to the Oracc build server which runs on Ubuntu and exposes an Apache web server. Ask a senior team member or Steve Tinney to get access to this server.

The following software needs to be installed on the Ubuntu server (ask Steve Tinney for help if you cannot install this software yourself):

1. `Git` (for cloning the website repo)
2. `python3`
3. `python3-pip`
4. `mod_wsgi` (for deploying the application. This may require a prior installation of the `apache2-dev` module to work properly, see [here](https://flask.palletsprojects.com/en/2.2.x/deploying/mod_wsgi/) for more instructions. This can be installed with: `sudo apt-get install apache2-dev`)

### Clone the repo

On the server, all our project code should be located at `/home/rits` and the Flask code is in the `/home/rits/oracc-rest` directory. If the `oracc-rest` folder does not already exit, you will need to clone the repo via git into `/home/rits`.

### Install python modules

Run the following command from the top-level directory of this repo:

```
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

### Spin up the Flask API in prod mode

Run the following from the top-level directory of this repo:

```
mod_wsgi-express start-server wsgi.py --port 5000 --processes 4
```

This will use the mod_wsgi package to spin up the Flask API as a Daemon process in the background on port 5000.

Note that if you press `ctrl+c` you will tear down the server. To leave it running while still being able to execute commands on the server, you can simply exit out of the terminal and log back in again. If you need to tear down the server in the future, you can kill the process by running:

```
sudo kill -9 `sudo lsof -t -i:5000`
```

You can test that the API is running by making a request to the test endpoint: `curl localhost:5000/test`. You will know the application is running if you get a "Hello world" response.

---

## Running the application: Flask API and Elasticsearch

Once you have set up your chosen environmnet (see above), you can then proceed to install all of the necessary packages for getting the application up and running:

### Installing jq

We use the [jq](https://stedolan.github.io/jq/) tool to efficiently preprocess large .json files to prepare them for upload into Elasticsearch. This can be easily installed through a package manager:

- OS X: `brew install jq`
- Ubuntu: `sudo apt-get install jq`

For more installation instructions and options, see [the tool's official page](https://stedolan.github.io/jq/download/).

### ElasticSearch management

To store Oracc's texts and their related metadata, we use [Elasticsearch](https://www.elastic.co/products/elasticsearch). The code in this repository has been tested with ElasticSearch 7.17.7.

To install ElasticSearch:

- OS X: `brew install elasticsearch`
- Ubuntu: see [this link with instructions](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html).

This API also requires the [ICU Analysis plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html).

To install the ICU Analysis Plugin:

- OS X: `elasticsearch-plugin install analysis-icu`
- Ubuntu: `sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install analysis-icu` (as per the link above)

Note that, after installing the plugin, if ElasticSearch was already running then each node has to be restarted. If running as a service (like in the instructions below), all nodes can be restarted with one command:

- OS X: `brew services restart elasticsearch`
- Ubuntu: `sudo service elasticsearch restart`

To launch an instance of Elasticsearch accessible in its default port 9200:

- OS X: `elasticsearch -d`
- Ubuntu: `systemctl start elasticsearch`

You can check Elasticsearch was successfully launched by running:

```
curl localhost:9200
```

The output should show something similar to this:

```
{
  "name" : "build-oracc",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "QnjkS8UATzCIIAil2HMAYQ",
  "version" : {
    "number" : "7.17.7",
    "build_hash" : "bd92e7f",
    "build_date" : "2017-12-17T20:23:25.338Z",
    "build_snapshot" : false,
    "lucene_version" : "8.11.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0"
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

- OS X: `pkill -f elasticsearch`
- Ubuntu: `systemctl stop elasticsearch`

---

## Indexing data into Elasticsearch

The purpose of this API is to return data related to translations of ancient texts. To make this data searchable via the API, we must first upload the data into an elasticsearch database.

The upload process assumes that data exists inside a `/neo` folder at the top-level directory of this repo. Note that the data in the `/neo` directory is currently only stored in the deployed production environment (i.e. on the Oracc Ubuntu server). The data can be provided in the correct format by Steve Tinney.

To upload the data into Elasticsearch, you can call the following utility function from the top-level directory of this repo:

```
python -m ingest.bulk_upload
```

This will ingest the data contained in the `/neo` folder into the Elasticsearch database.

The [ingest](ingest) folder also has some additional information and alternative ways of performing the indexing.

**NB**: At the moment, ingesting the data first deletes any previous version of it that may exist on the Elasticsearch instance, rather than updating it!

Once the data is indexed, it can be queried with Elasticsearch directly (either through the Flask API or from the command line, by sending HTTP requests with `curl`).

---

## Additional infor for querying the Flask API

### Calling the Flask API endpoints to retrieve data from Elasticsearch

The search can be accessed at the `/search` endpoint of a server running Elasticsearch and the Oracc web server in this repo, e.g.:

```
curl -XGET localhost:5000/search/water
```

This searches multiple fields for the given query word and returns all results. The list of fields currently searched is: `gw` (guideword), `cf` (cuneiform), `senses.mng` (meaning), `forms.n` and `norms.n` (lemmatisations).

The matching is not exact: an entry is considered to match a query word if it contains any term starting with the query in the relevant fields. For example, searching for "cat" would return words with either "cat" or "catch" in their meanings (among others).

The query can also be a phrase of words separated by spaces. In this case, it will return results matching **all** of the words in the phrase.

A second endpoint at `/search_all` can be used to retrieve all indexed entries.

In both cases, the result is a JSON array with the full contents of each hit. If no matches are found, a 204 (No Content) status code is returned.

An older, simpler search mode can also be accessed at the `/search` endpoint:

```
curl -XGET localhost:5000/search -d 'gw=water'
```

This mode supports searching a single field (e.g. guideword) for the given value. If more than one fields are specified (or if none are), an error will be returned. This does not accept the extra parameters described below, and should be considered deprecated.

### Customising the search

You can customise the search by optionally specifying additional parameters.

These are:

- `sort_by`: the field on which to sort (`gw`, `cf` or `icount`)
- `dir`: the sorting order, ascending (`asc`) or descending (`desc`)
- `count`: the maximum number of results

For example, if you want to retrieve the 20 entries that appear most frequently in the indexed corpus, you can request this at:

```
localhost:5000/search_all?sort_by=icount&dir=desc&count=20
```

### Paginating the results

If you don't want to retrieve all results at once, you can use a combination of the `count` parameter described above and the `after` parameter. The latter takes a "sorting threshold" and only returns entries whose sorting score is greater or lesser (for ascending or descending search, respectively) than this threshold.

### Suggesters

Two other end points can be accessed at the `/suggest` and `/completion` endpoints of a server running ElasticSearch and the Oracc web server in this repo.

In the case of `/suggest` e.g.:

```
curl -XGET localhost:5000/suggest/yam
```

This searches both `gw` (guideword) and `cf` (cuneiform) fields for words which are within a distance of 2 changes from the query word, e.g.: `yam` returns `ym` and `ya` (`cf`).

In the case of `/completion` e.g.:

```
curl -XGET localhost:5000/completion/go
```

This searches both `gw` (guideword) and `cf` (cuneiform) fields for words which begin with the query. This works for single letters or fragments of words. e.g.: `go` returns `god` and `goddess`

**Important note**: The sorting score depends on the field being sorted on, but it is _not_ equal to the value of that field! Instead, you can retrieve an entry's score by looking at the `sort` field returned with each hit. You can then use this value as the threshold when requesting the next batch of results.

---

## Running the tests

The code is accompanied by tests written for the [pytest](https://pytest.org) library (installed with the requirements), which can help ensure that important functionality is not broken.

To run the tests after making changes, execute the following from the top-level directory of this repo:

```
python -m pytest tests
```
