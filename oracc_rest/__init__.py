from flask import abort, Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource

from .search import ESearch


app = Flask(__name__)
CORS(app)
api = Api(app)


class SingleFieldSearch(Resource):
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
        results = search.run(word, fieldname)
        # Return search results to caller
        if not results:
            return {}, 204  # "empty content" response if no results found
        return results


class GeneralSearch(Resource):
    def get(self, word):
        """Search "all" fields in the database for the given word."""
        # Pass to ElasticSearch
        search = ESearch()
        results = search.run(word)
        # Return search results to caller
        if not results:
            return {}, 204  # "empty content" response if no results found
        return results


class FullList(Resource):
    def get(self):
        """Search "all" fields in the database for the given word."""
        # Pass to ElasticSearch
        search = ESearch()
        results = search.list_all()
        # Return search results to caller
        return results


# Make the search API available at the "/search" endpoint
api.add_resource(SingleFieldSearch, '/search')
api.add_resource(GeneralSearch, '/search/<string:word>')
api.add_resource(FullList, '/search_all')
