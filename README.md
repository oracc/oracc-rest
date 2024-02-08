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

The Oracc project needs both Flask and Elasticsearch to be installed to run correctly. Therefore, this guide will take you through the following steps:

1. Setting up the Oracc project on a development and/or production environment.
2. Installing elasticsearch on each environment.

We will first take you through setting up your development and production environments by spinning up the Flask API. Once this has been done you can proceed to the section describing how to set up Elasticsearch.

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

## Setting up the project on Ubuntu (for either development or production)

The production version of this project is deployed on Ubuntu on a remote server. However, we recommend setting up a virtual instance of Ubuntu on your local machine first (using Multipass) as this will allow you to test out the entire deployment process and learn how it works before doing it for real on prod. It's up to you if you want to do this or not, so if you just want to skip ahead to the main production deployment instructions you can go to [Spinning up Flask on Ubuntu](#spinning-up-flask-on-ubuntu).

### Setting up a virtual Ubuntu instance on your local machine using Multipass

You can easily spin up a local virtual Ubuntu server using [Multipass](https://multipass.run/). Multipass is a piece of software used specifically for creating local virtual instances of Ubuntu. To get started with this, follow the steps below:

### Install Multipass

Install Multipass on your local machine using the [instructions](https://multipass.run/) on their website.

You should now have access to the Multipass commands in your terminal. To check that it is installed correctly, open a terminal and run: `multipass version`

### Create a new virtual Ubuntu instance

To create a virtual Ubuntu instance on your local machine, use the below commands in your terminal:

1. `multipass launch --name <your-instance-name>` - creates a new Multipass virtual Ubuntu instance.
2. `multipass shell <your-instance-name>` - opens a shell inside your Ubuntu instance so you can start interacting with it.

You can now do whatever you need to inside the virtual Ubuntu instance such as installing the software needed to get the Oracc development environment set up (see instructions below).

### Useful Multipass commands

`multipass list` - returns the list of virtual Ubuntu instances that you have activated (see below for instructions on how to make new virtual environments).

`multipass info <instance-name>` - Returns information about a specific instance.

`multipass suspend <instance-name>` - Suspend an instance and keep its current state.

`multipass stop <instance-name>` - Stops an instance without preserving its state.

`multipass delete <instance-name>` - Deletes a stopped instance.

`multipass purge` - Completely removes deleted instances.

---

## Spinning up Flask on Ubuntu

During development, the application can be deployed on a Multipass virtual Ubuntu instance as suggested above.

For production, the application is currently deployed to the Oracc build server (more details on the [ORACC Server wiki](https://github.com/oracc/website/wiki/ORACC-Server)) which runs on Ubuntu and exposes an Apache web server. Ask a senior team member or Steve Tinney to get access to this server.

### Connect to the server

For development, you should open a new shell into your Multipass instance.

For production, you should SSH into the Oracc server, ask a senior team member how to do this.

Once you are connected, it's always a good idea to update packages as a first step: `sudo apt-get update && sudo apt-get upgrade -y`

### Install software

The following software needs to be installed on Ubuntu:

1. **Git** - for cloning the website repo: `sudo apt install git`
2. **python3** - for running the Flask app: `sudo apt install python3.10` (_note_ if python is already installed on the sever just use that version)
3. **python3-pip** - for installing python modules: `sudo apt install python3-pip`
4. **mod_wsgi** - tells apache how to host the Flask app: `sudo apt install libapache2-mod-wsgi-py3`
5. **apache2** - the web server that will handle http requests: `sudo apt install apache2`

As soon as apache is installed, a web server should now be exposed and accessible via the IP address of the host server. During development, the IP address of your Multipass virtual Ubuntu server can be found by running `multipass list` in a local terminal. If its working, you should get the default apache web page when accessing the IP address in a web browser.

### Enable wsgi on apache

Once the above software has been installed, you then need to enable wsgi within apache: `sudo a2enmod wsgi`

### Create a workspace folder and set access permissions

Our project code should be located in `/home/rits`. Go ahead and make this folder if it doesn't already exist.

You may also need to set the appropriate access permissions. On your development environment you can simply run the following command: `sudo chmod a+rwx /home/rits`. But on production you should ask a senior member (e.g. Steve Tinney) to do this for you.

### Clone the repo

Clone the repo into the `/home/rits` folder you just made. You should end up with the Flask code inside the `/home/rits/oracc-rest` directory.

For a development environment, you may need to clone the repo over `https` instead of `ssh`. For production, `ssh` should be fine as long as your ssh keys have been properly configured.

The production deployment should run from the `main` branch of this repo.

### Install python modules

First, create and activate a python virtual environment in `/home/rits/oracc-rest`:

```sh
sudo apt install python3.10-venv
python3 -m venv venv # run this if the environment does not already exist, note the lack of sudo here to avoid issues
source venv/bin/activate # activates the environment
```

You can deactivate a virtual environment simply by entering `deactivate` in the terminal.

If you run into an issue here, you may need to set the appropriate permissions on some directories if you are getting a 'permission denied error', ask Steve Tinney to do this. Also see [this thread](https://stackoverflow.com/questions/19471972/how-to-avoid-permission-denied-when-using-pip-with-virtualenv) for fixing a common issue when setting up a virtual environment.

Once your virtual environment is activated, run the following command from `/home/rits/oracc-rest`:

```sh
pip install -r requirements.txt
```

This will install modules related to both Flask and Elasticsearch.

### Link the Flask folder to an Apache directory

The Flask app folder needs to be linked to an Apache directory to correctly expose the API endpoints. This is done by creating a symlink with the following command: `sudo ln -sT /home/rits/oracc-rest /var/www/oracc-rest`

Then, add the following Apache config file by running: `sudo nano /etc/apache2/sites-available/oracc-rest.conf`:

```apacheconf
<VirtualHost *:5000>
  ServerAdmin stinney@upenn.edu
  ServerName build-oracc.museum.upenn.edu

  ErrorLog ${APACHE_LOG_DIR}/oracc-rest_error.log
  CustomLog ${APACHE_LOG_DIR}/oracc-rest_access.log combined

  # These next 3 lines are only needed (uncommented) on the production machine
  #SSLEngine On
  #SSLCertificateKeyFile /etc/ssl/private/build-oracc.key
  #SSLCertificateFile /etc/ssl/certs/build-oracc.pem

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

Then, to enable the config you need to run:

```sh
sudo a2enmod ssl
sudo a2ensite oracc-rest.conf
```

This configuration will allow the mod_wsgi package to talk to apache and expose the Flask API endpoints on port 5000. The config is read automatically as apache starts up, so any changes will require you to restart apache.

### Open the necessary ports in apache

The application is now set up to respond to requests at port 5000, but you still need to open the port to let the requests come through in apache. You can ask Steve Tinney to open the necessary ports, or ensure that the following code is present in
the file `/etc/apache2/ports.conf`:

```apacheconf
Listen 80
Listen 5000
```

Apache will need to be restarted following any config modifications. You can restart Apache with the following: `sudo systemctl restart apache2`

You can test that the API is running by making a request on the server to the test endpoint:

During local development, run: `curl http://localhost:5000/test`.

During production, run: `curl -k https://localhost:5000/test`.

You should get a "Hello world" response.

### Troubleshooting

If there are any problems you can try the following steps:

Check the status of apache: `systemctl status apache2.service`.

Check apache error logs: `sudo nano /var/log/apache2/error.log`.

Check that the necessary ports are open: `telnet localhost 5000`, if the port is not open you should get a failed to connect message.

Check Flask error logs: `sudo nano /var/log/apache2/oracc-rest_error.log`

Check Flask network requests: `sudo nano /var/log/apache2/oracc-rest_access.log`

---

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

Ingest from the same directory again, and get logs from that (from any directory):

```sh
docker restart oracc-ingest
docker logs -t oracc-ingest
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

### Option 2: Install elasticsearch on Ubuntu

Use this option if you are deploying to production, or are testing out the application using Multipass as described above.

To get elasticsearch up and running directly on Ubuntu follow the below instructions:

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
- Ubuntu: see [this link with instructions](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/deb.html).

This API also requires the [ICU Analysis plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-icu.html).

To install the ICU Analysis Plugin:

- OS X: `elasticsearch-plugin install analysis-icu`
- Ubuntu: `sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install analysis-icu` (as per the link above)

To remove the ICU Analysis Plugin:

- Ubuntu: `sudo /usr/share/elasticsearch/bin/elasticsearch-plugin remove analysis-icu`

Note that, after installing the plugin, if ElasticSearch was already running then each node has to be restarted. If running as a service (like in the instructions below), all nodes can be restarted with one command:

- OS X: `brew services restart elasticsearch`
- Ubuntu: `sudo systemctl restart elasticsearch`

To launch an instance of Elasticsearch accessible in its default port 9200:

- OS X: `elasticsearch -d`
- Ubuntu: `sudo systemctl start elasticsearch`

You can check Elasticsearch was successfully launched by running:

```
curl localhost:9200
```

The output should show something similar to this:

```
{
  "name" : "build-oracc",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "bb2yg_3zTuG3Zjbav4QlTg",
  "version" : {
    "number" : "7.17.11",
    "build_flavor" : "default",
    "build_type" : "deb",
    "build_hash" : "eeedb98c60326ea3d46caef960fb4c77958fb885",
    "build_date" : "2023-06-23T05:33:12.261262042Z",
    "build_snapshot" : false,
    "lucene_version" : "8.11.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
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
oracc analysis-icu 7.17.11   The ICU Analysis plugin integrates Lucene ICU module into elasticsearch, adding ICU relates analysis components.
```

To stop ElasticSearch:

- OS X: `pkill -f elasticsearch`
- Ubuntu: `sudo systemctl stop elasticsearch`

### Prevent automatic updates of Elasticsearch on Ubuntu

Occasionally, Elasticsearch may get updated on Ubuntu automatically.

To stop ElasticSearch automatically updating and becoming incompatible with the installed ICU plugin, run:

- Ubuntu: `sudo apt-mark hold elasticsearch`

If you run into a situation where Elasticsearch has been updated on the server then the analysis-icu plugin may no longer be compatible. In this case, you will need to update the analysis-icu plugin using the following steps: 1. stop the current Elasticsearch service, 2. remove the analysis-icu plugin (see instructions above), 3. Reinstall the analysis-icu plugin (see instructions above), 4. Start the Elasticsearch service.

### Troubleshooting

If there are any issues, try the following:

Check Elasticsearch status: `systemctl status elasticsearch.service`

Check Elasticsearch logs: `sudo nano /var/log/elasticsearch/elasticsearch.log`.

---

## Indexing data into Elasticsearch

Now that Elasticsearch has been set up either using Docker (for development) or Ubuntu, you can start to upload glossary data into the Elasticsearch database.

Some test datasets have been provided at: `ingest/assets/dev/sample-glossaries`, you can use this data to test out the elasticsearch functionality on your development environment (make sure you do not ingest this data on the production database).

The production glossary data is provided by the PI's in the correct format, so ask Steve Tinney or Eleanor Robson for more details.

To upload the data into the Elasticsearch database, you can call the following utility function from the top-level directory of this repo:

Note the lack of `sudo` in the below command to make sure that the script reads from the virtual environment that was created earlier.

```
python3 -m ingest.bulk_upload ingest/assets/dev/sample-glossaries/*
```

If no arguments are provided, then the function will try to upload the glossary files located in a `/neo` folder at the top-level directory of this repo.

The [ingest](ingest) folder also has some additional information and alternative ways of performing the indexing.

**NB**: At the moment, ingesting the data first deletes any previous version of it that may exist on the Elasticsearch instance, rather than updating it!

Once the data is indexed, it can be queried with Elasticsearch directly (either through the Flask API or from the command line, by sending HTTP requests with `curl`).

---

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
