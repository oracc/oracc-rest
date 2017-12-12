A RESTful API for querying the ORACC database using ElasticSearch.

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

In either search mode, each hit is returned as a dictionary comprising the
headword, gw and cf fields.
