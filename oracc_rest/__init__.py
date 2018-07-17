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
        """Return all entries in the database.

        Optionally search within a specific range of entries, by passing a
        starting index (start) and the desired number of results (count)."""
        # See if the user has asked for pagination
        try:
            start = int(request.args['start'])
            count = int(request.args['count'])
        except (KeyError, ValueError):
            start, count = None, None
        # Sort by the cf field unless otherwise specified
        sort_field = request.args.get('sort_by', 'cf')
        # Sort in ascending order unless otherwise specified
        # TODO Throw an error if invalid direction is given? Be more flexible
        # (e.g. accept "ascending" as a synonym of "asc")?
        dir = request.args.get('dir', 'asc')
        # See if a starting point has been specified
        after = request.args.get('after', None)
        # Pass to ElasticSearch
        search = ESearch()
        results = search.list_all(sort_field, dir, start, count, after)
        # Return search results to caller
        return results


# Make the search API available at the "/search" endpoint
api.add_resource(SingleFieldSearch, '/search')
api.add_resource(GeneralSearch, '/search/<string:word>')
api.add_resource(FullList, '/search_all')
