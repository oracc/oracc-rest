from urllib.parse import unquote

from flask import abort, Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource

from .search import ESearch

app = Flask(__name__)
CORS(app)
api = Api(app)


def _parse_request_args(args):
    """Retrieve the options of interest from a dictionary of arguments.

    If any expected options are not found, they will just not be copied over.
    Unexpected parameters are simply ignored.
    """
    out_args = {}
    string_options = ["sort_by", "dir", "after"]
    for option in string_options:
        if option in args:
            # TODO Throw an error if invalid values are given? Be more flexible?
            # (e.g. accept "ascending" as a synonym of "asc")
            # It seems that Flask automatically un-escapes spaces in the request
            # parameters, but I couldn't find any docs for it. Just in case some
            # characters are not handled (remember that some glossary entries
            # contain "weird" characters), we explicitly un-escape the arguments
            # here.
            out_args[option] = unquote(args[option])
    # See if the user has specified how many results to retrieve
    # (we do this separately as we have to convert it to an integer)
    try:
        out_args["count"] = int(args["count"])
    except (KeyError, ValueError):
        pass
    return out_args


def _all_suggest_compiler(completions, suggestions):
    """This combines the suggestions and completions into
    a dictionary which can be displayed."""
    format_results = {"completions": completions, "suggestions": suggestions}
    return format_results


class SingleFieldSearch(Resource):
    def get(self):
        args = request.form
        # Parse request
        if not args:
            abort(400, "No query specified!")
        elif len(args) > 1:
            abort(400, "Too many fields specified!")
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
        args = _parse_request_args(request.args)
        # Pass to ElasticSearch
        search = ESearch()
        results = search.run(word, **args)
        # Return search results to caller
        if not results:
            return {}, 204  # "empty content" response if no results found
        return results


class Suggestion(Resource):
    def get(self, word):
        """Get suggestions for terms similar to a (possibly partial) word."""
        args = _parse_request_args(request.args)
        if "count" in args:
            size = args["count"]
        else:
            size = 100
        search = ESearch()
        results = search.suggest(word, size)
        return results


class Completion(Resource):
    def get(self, word):
        """Get completions for partial words."""
        args = _parse_request_args(request.args)
        if "count" in args:
            size = args["count"]
        else:
            size = 200
        search = ESearch()
        results = search.complete(word, size)
        return results


class CombinedSuggestions(Resource):
    def get(self, word):
        """Call both completion and suggestion methods

        This also then uses a function to combine the results into
        a dictionary"""
        args = _parse_request_args(request.args)
        if "count" in args:
            c_size = s_size = args["count"]
        else:
            c_size = 200
            s_size = 100
        search = ESearch()

        completions = search.complete(word, c_size)
        suggestions = search.suggest(word, s_size)
        results = _all_suggest_compiler(completions, suggestions)
        return results


class FullList(Resource):
    def get(self):
        """Return all entries in the database.

        Optionally search within a specific range of entries, by passing a
        starting index (start) and the desired number of results (count).
        """
        args = _parse_request_args(request.args)
        # Pass to ElasticSearch
        search = ESearch()
        results = search.list_all(**args)
        # Return search results to caller
        return results


# Make the search API available at the "/search" and "/suggest" endpoints
api.add_resource(SingleFieldSearch, "/search")
api.add_resource(GeneralSearch, "/search/<string:word>")
api.add_resource(FullList, "/search_all")
api.add_resource(Suggestion, "/suggest/<string:word>")
api.add_resource(Completion, "/completion/<string:word>")
api.add_resource(CombinedSuggestions, "/suggest_all/<string:word>")
