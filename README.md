# Oracc REST

A Flask RESTful API for querying the Oracc database using Elasticsearch.

The accompanying frontend project for accessing this backend can be found [on this repo](https://github.com/oracc/oracc-search-front-end).

The guide below is sufficient for setting up the entire project. For additional technical and supplementary information please refer to the [ORACC Server wiki](https://github.com/oracc/website/wiki/ORACC-Server).

You can also see [these useful snippets](https://github.com/oracc/oracc-rest/wiki/Useful-snippets).

This codebase has been written and tested in Python3.

---

## Project structure

This is the directory structure in the project root:

```bash
.
├── api # flask API code
├── ingest # scripts for processing and uploading data into elasticsearch
├── tests # custom tests
├── app.py # entrypoint for running the flask api
├── oracc-rest.wsgi # config file for serving the flask api via apache
└── requirements.txt # list of python modules used by the project

```

---

## Setting up the project

The Oracc project has been dockerised to run Flask and ElasticSearch

### Using a python virtual environment

It is best practice to work within a python virtual environment for both development and production. This keeps any packages you install isolated from any system-wide installations. You can use any virtual environment manager of your choice, but make sure not to commit your virtual environment folder to this repo. Here is an example using the built-in python virtual environment manager:

```sh
# run the following from the top-level directory of your python project
python3 -m venv env-name # creates the environment
source venv/bin/activate # activates the environment
deactivate # deactivates the environment
```

Once you have created and activated your virtual environment, you can install pip packages and do all other tasks as normal.

---

## Spinning up Flask for development on your local machine

This approach can be used if you want to activate the Flask API directly on your local machine. This is usually the quickest and easiest method for getting started. But if you also want the Flask API to communicate with elasticsearch on your local development machine then please follow the instructions further below for [Exposing a Dockerised instance of elasticsearch](#option-1-expose-a-dockerised-instance-of-elasticsearch).

### Install dependencies

Run the following command from the top level directory of this repo (preferably within a virtual python environment):

```sh
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

### Activate Flask in debug mode

From the top-level directory of this repo, run:

```sh
flask --app app --debug run --port 8000
```

This will start the server in development mode on port 8000 and expose the endpoints. To run the server on a different port, specify (e.g.) `--port 3000`.

You can test that the API is running by making a request to the test endpoint: `localhost:8000/test`. You should get a "Hello world!!!!!" response.

Any changes to the code should be picked up automatically and make the server restart.

You can stop the server with `ctrl+c`

Do not use the development server when deploying to production. It is intended for use only during local development.

---

## Spinning up Flask on Ubuntu

During development, the application can be deployed on a Multipass virtual Ubuntu instance as suggested above.

For production, the application is currently deployed to the Oracc build server (more details on the [ORACC Server wiki](https://github.com/oracc/website/wiki/ORACC-Server)) which runs on Ubuntu and exposes an Apache web server. Ask a senior team member or Steve Tinney to get access to this server.

## Installing and configuring Elasticsearch

Now that the API is up and running in either development or production mode, you can install Elasticsearch so that you can hit the `/search` API endpoints to return the Oracc data.

### Option 1: Expose a Dockerised instance of elasticsearch

Use this option if you are spinning up a completely local instance of the project for development. This option works well if you are spinning up the Flask app in debug mode as described in the section above: [Activate Flask in debug mode](#activate-flask-in-debug-mode).

Make sure you have Docker installed on your local machine first.

Then you can simply get elasticsearch and the api server up and running with the following command from the top-level directory of this repo:

```
docker-compose up --build -d
```

This will expose the api server on `localhost:8000`. The elasticsearch
server will be populated with the glossaries, and the api server will
be connected with elasticsearch. Elasticsearch will not be available
from outside the docker network.

To stop the Docker container run `docker-compose down`

#### Using docker-compose in production

The docker-compose deployment uses gunicorn and is production-ready.
However, you need to change the port to 5000 and the ingest directory
(from the root of the source directory):

```sh
ORACC_INGEST_DIRECTORY=/path/to/ingest ORACC_PORT=5000 docker-compose up --build -d
```

Of course it is better to set `ORACC_PORT` and `ORACC_INGEST_DIRECTORY` in your `~/bash.rc` or wherever you prefer, rather than having to set them on the command line each time. I will continue to show them on the command line, however.

Ingest from the same directory again, and get logs from that (from any directory):

```sh
docker restart oracc-ingest
docker logs --tail=30 -t oracc-ingest
```

If you want to change the ingest directory, you must remove the old volume and restart. The easiest way would be:

```sh
docker-compose down -v
ORACC_INGEST_DIRECTORY=/path/to/ingest ORACC_PORT=5000 docker-compose up --build -d
```

This will destroy all the existing elasticsearch data and recreate it. If you would rather not recreate all the data, do this:

```sh
docker-compose down
docker rm oracc-ingest
docker volume rm oracc-rest_ingest
ORACC_INGEST_DIRECTORY=/path/to/ingest ORACC_PORT=5000 docker-compose up --build -d
```

The elastic search data is persistent across restarts. To remove it (again from
the source directory):

```sh
docker-compose down -v
ORACC_INGEST_DIRECTORY=/path/to/ingest ORACC_PORT=5000 docker-compose up --build -d
```

## Additional info for querying the Flask API

### Calling the Flask API endpoints to retrieve data from Elasticsearch

The search can be accessed at the `/search` endpoint of a server running Elasticsearch and the Oracc web server in this repo, e.g.:

```shell
# during production
curl -k https://localhost:5000/search/water-skin

# during development
curl http://localhost:5000/search/water-skin
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
- `direction`: the sorting order, ascending (`asc`) or descending (`desc`)
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
