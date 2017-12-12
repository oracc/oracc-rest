from flask import Flask, request, abort
from flask_restful import Resource, Api

from .search import ESearch


app = Flask(__name__)
api = Api(app)


class OraccREST(Resource):
    def get(self):
        args = request.form
        # Parse request
        if not args:
            abort(400, 'No query specified!')
        elif len(args) > 1:
            abort(400, 'Too many fields specified!')
        fieldname, word = list(args.items())[0]
        # Pass to ElasticSearch
        search = ESearch()
        results = search.run(fieldname, word)
        # Return search results to caller
        if not results:
            return {}, 204  # "empty content" response if no results found
        return results


# Make the search API available at the "/search" endpoint
api.add_resource(OraccREST, '/search')
