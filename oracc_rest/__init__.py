from flask import Flask, jsonify, request

from .search import ESearch


app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route('/search')
def search_field():
    """Search the databse for occurences of a word in a specified field."""
    args = request.form
    # Parse request
    if not args:
        return jsonify([])
        # return 'No query specified!', 400
    elif len(args) > 1:
        return jsonify([])
        # abort(400, 'Too many fields specified!')
    fieldname, word = list(args.items())[0]
    # Pass to ElasticSearch
    search = ESearch()
    results = search.run(word, fieldname)
    # Return search results to caller
    if not results:
        return jsonify([])
        # return {}, 204  # "empty content" response if no results found
    return jsonify(results)


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
