import json

from flask import Flask, jsonify

from .search import ESearch


app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route('/search/<word>')
def general_search(word):
    """Search "all" fields in the database for the given word."""
    # Pass to ElasticSearch
    search = ESearch()
    results = search.run(word)
    # Return search results to caller
    if not results:
        return ''
    return jsonify(results)


@app.route('/search_all')
def all_entries():
    """Search "all" fields in the database for the given word."""
    # Pass to ElasticSearch
    search = ESearch()
    results = search.list_all()
    # Return search results to caller
    return jsonify(results)


# class SingleFieldSearch(Resource):
#     def get(self):
#         args = request.form
#         # Parse request
#         if not args:
#             abort(400, 'No query specified!')
#         elif len(args) > 1:
#             abort(400, 'Too many fields specified!')
#         fieldname, word = list(args.items())[0]
#         # Pass to ElasticSearch
#         search = ESearch()
#         results = search.run(word, fieldname)
#         # Return search results to caller
#         if not results:
#             return {}, 204  # "empty content" response if no results found
#         return results


# Make the search API available at the "/search" endpoint
# api.add_resource(SingleFieldSearch, '/search')
# api.add_resource(GeneralSearch, '/search/<string:word>')
# api.add_resource(FullList, '/search_all')
