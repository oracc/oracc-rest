# Oracc REST

A Flask RESTful API for querying the Oracc database using Elasticsearch.

The accompanying frontend project for accessing this backend can be found [here](https://github.com/oracc/oracc-search-front-end).

This codebase has been written and tested in Python3.

The guide below is sufficient for setting up the entire project. For additional technical and supplementary information please also refer to [this](https://github.com/oracc/website/wiki/ORACC-Server) wiki.

---

## Setting up a development and production environment

This application needs both Flask and Elasticsearch to be installed to run correctly. Therefore, this guide will take you through the following steps:

1. Setting up Flask on a development and/or production environment.
2. Installing elasticsearch on each environment.

We will first take you through setting up your environments and spinning up the Flask API. Once this has been done you can proceed to the section describing how to set up Elasticsearch.

It is also best practice to work within a python virtual environment for both development and production. This keeps any packages you install isolated from any system-wide installations. You can use any virtual environment manager of your choice, but make sure not to commit your virtual environment folder to this repo.

---

## Development environment

While you can run this application directly on your local machine, you may wish to set up a virtual Ubuntu server for testing the application locally during development. This is preferable as it mimics the production environment more closely (see below). You can easily spin up a local virtual Ubuntu server using [Multipass](https://multipass.run/), although its usage is beyond the scope of this readme.

To start, clone the repo to your local machine or virtual Ubuntu server (you will need Git and Python3 installed at the very least).

### Install python modules

Within your own python virtual environment, run the following command from the top-level directory of this repo:

```
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

### Spin up the Flask API in dev mode

To enable the search endpoints described below, the Flask server must be started. To do this, from the top-level directory run:

```
flask --app app --debug run --port 8000
```

This will start the server in development mode on port 8000 and expose the endpoints. To run the server on a different port, specify (e.g.) `--port 3000`.

You can test that the API is running by making a request to the test endpoint: `localhost:8000/test`. You should get a "Hello world" response.

Any changes to the code should be picked up automatically and make the server restart.

You can stop the server with `ctrl+c`

Do not use the development server when deploying to production. It is intended for use only during local development.

---

## Production environment

The application is currently deployed for production to the Oracc build server (more details [here](https://github.com/oracc/website/wiki/ORACC-Server)) which runs on Ubuntu and exposes an Apache web server. Ask a senior team member or Steve Tinney to get access to this server.

Once you are connected to the server it's always a good idea to update the packages as a first step: `sudo apt-get update && sudo apt-get upgrade -y`

You may need to restart apache after running certain commands along the way, you can do this with: `sudo service apache2 restart`

### Install software

The following software needs to be installed on the Ubuntu server:

1. **Git** - for cloning the website repo: `sudo apt install git`
2. **python3** - for running the Flask app: `sudo apt install python3.8`
3. **python3-pip** - for installing python modules: `sudo apt install python3-pip`
4. **mod_wsgi** - tells apache how to host the Flask app: `sudo apt install libapache2-mod-wsgi-py3`
5. **apache2** - the web server that will handle http requests: `sudo apt install apache2` (_note_ this should already be installed on the server, included here for documentation)

### Enable wsgi on apache

Once the above software has been installed, you then need to enable wsgi within apache: `sudo a2enmod wsgi`.

### Clone the repo

On the Ubuntu server, our project code should be located at `/home/rits` so this is where you should clone the project into. You should end up with the Flask code inside the `/home/rits/oracc-rest` directory.

### Install python modules

First, create and activate a python virtual environment from the top-level directory of this repo:

```python
python3 -m venv venv # run this if the environment does not already exist
source venv/bin/activate # activates the environment
```

You may need to set the appropriate permissions on some directories if you are getting a 'permission denied error', ask Steve Tinney to do this. Also see [here](https://stackoverflow.com/questions/19471972/how-to-avoid-permission-denied-when-using-pip-with-virtualenv) for fixing a common issue when setting up a virtual environment.

Once your virtual environment is activated, run the following command from the top-level directory of this repo:

```
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

### Link the Flask folder to an Apache directory

The Flask app folder needs to be linked to an Apache directory to correctly expose the API endpoints. This is done by creating a symlink with the following command: `sudo ln -sT /home/rits/oracc-rest /var/www/oracc-rest`.

Then, add the following Apache config file by running: `sudo nano /etc/apache2/sites-available/oracc-rest.conf`:

```apacheconf
<VirtualHost *:5000>
  ServerAdmin stinney@upenn.edu
  ServerName build-oracc.museum.upenn.edu

  ErrorLog ${APACHE_LOG_DIR}/oracc-rest_error.log
  CustomLog ${APACHE_LOG_DIR}/oracc-rest_access.log combined

  # remove these next three lines if you are not running the app over HTTPS
  SSLEngine On
  SSLCertificateKeyFile /etc/ssl/private/build-oracc.key
  SSLCertificateFile /etc/ssl/certs/build-oracc.pem

  WSGIDaemonProcess oracc-rest threads=5 python-home=/var/www/oracc-rest/venv
  WSGIScriptAlias / /var/www/oracc-rest/oracc-rest.wsgi
  WSGIApplicationGroup %{GLOBAL}

  <Directory /var/www/oracc-rest>
    WSGIProcessGroup oracc-rest
    Order deny,allow
    Allow from all
  </Directory>
</VirtualHost>
```

Then, to enable the config you need to run: `sudo a2ensite oracc-rest.conf`

This configuration will allow the mod_wsgi package to talk to apache and expose the Flask API endpoints on port 5000.

### Open the necessary ports in apache

The application is now set up to respond to requests at port 5000, but you still need to open the port to let the requests come through in apache. You can ask Steve Tinney to open the necessary ports, or add the following code to the file `/etc/apache2/ports.conf`:

```apacheconf
Listen 80
Listen 5000
```

Apache will need to be restarted following any config modifications. You can restart Apache with the following: `sudo service apache2 restart` .

You can test that the API is running by making a request on the server to the test endpoint: `curl -k https://localhost:5000/test`. You should get a "Hello world" response.

### Troubleshooting

If there are any problems, check errors here: `/var/log/apache2/error.log`. You can also check the status of apache by entering: `systemctl status apache2.service`. You can also check if ports are open with: `telnet localhost 5000`, if the port is not open you should get a failed to connect message.

---

## Installing and configuring Elasticsearch

Now that the API is up and running in either development or production mode, you can install Elasticsearch so that you can hit the `/search` API endpoints to return the Oracc data.

To set up Elasticsearch, the following software needs to be installed on your current development or production environment.

### Installing jq

We use the [jq](https://stedolan.github.io/jq/) tool to efficiently pre-process large .json files to prepare them for upload into Elasticsearch. This can be easily installed through a package manager:

- OS X: `brew install jq`
- Ubuntu: `sudo apt-get install jq`

For more installation instructions and options, see [the tool's official page](https://stedolan.github.io/jq/download/).

You can check that jq has been installed with `jq --version`

### ElasticSearch management

To store Oracc's texts and their related metadata, we use [Elasticsearch](https://www.elastic.co/products/elasticsearch). The code in this repository has been tested with ElasticSearch 7.17.7.

To install ElasticSearch:

- OS X: `brew install elasticsearch`
- Ubuntu: see [this link with instructions](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/install-elasticsearch.html).

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

_\*\*NOTE this section currently only applies to the production environment. Future instructions will be added for setting this up locally._

Now that Elasticsearch has been set up, you can start to upload data into the Elasticsearch database.

The upload process assumes that data exists inside a `/neo` folder at the top-level directory of this repo.

Note that the data in the `/neo` directory is currently only stored in the deployed production environment (i.e. on the Oracc Ubuntu server). The data can be provided in the correct format by Steve Tinney.

To upload the data into Elasticsearch, you can call the following utility function from the top-level directory of this repo:

```
python -m ingest.bulk_upload
```

This will ingest the data contained in the `/neo` folder into the Elasticsearch database.

The [ingest](ingest) folder also has some additional information and alternative ways of performing the indexing.

**NB**: At the moment, ingesting the data first deletes any previous version of it that may exist on the Elasticsearch instance, rather than updating it!

Once the data is indexed, it can be queried with Elasticsearch directly (either through the Flask API or from the command line, by sending HTTP requests with `curl`).

---

## Additional info for querying the Flask API

### Calling the Flask API endpoints to retrieve data from Elasticsearch

The search can be accessed at the `/search` endpoint of a server running Elasticsearch and the Oracc web server in this repo, e.g.:

```
curl -k https://localhost:5000/search/water-skin
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
