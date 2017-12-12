A RESTful API for querying the ORACC database using ElasticSearch.

The search can be accessed at the `/search` endpoint of a server running
ElasticSearch, e.g.:

```curl -XGET localhost:5000/search' -d 'headword=water'```

Currently, the server supports searching a single field (e.g. headword) for the
given value. If more than one fields are specified (or if none are), an error
will be returned.
