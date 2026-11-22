# rssources used for this file :
    
    # understanding isinstance() : https://www.youtube.com/watch?v=7hQhEoMyB04
    # dictionary in python : https://www.youtube.com/watch?v=a10AeJ_o-44&t=443s (same that in csv_loader)
    # string comparison : https://www.youtube.com/watch?v=upIvWNd8dZY
    

from validator import _parse_datetime   # check that a datetime is valid

# the 6 infos of a flight

record_keys = ["flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price"]

# keys that are in text
string_keys = ["flight_id", "origin", "destination"]

# keys that are a datetime
datetime_keys = ["departure_datetime", "arrival_datetime"]

# keys that are a number
number_keys = ["price", "min_price"]

# all the keys allowed in a query
allowed_keys = record_keys + ["min_price", "sort_by", "order", "limit"]


def _is_number(value) -> bool :
    
    """it's true if value is a number either int or float """

    # True and False count as int in Python, so we refuse them first
    if isinstance(value, bool) :
        return False

    return isinstance(value, (int, float))


def _is_valid_query(query) -> bool :
    """if the query respects all the rules it's true if not it's false """

    # a query must be a dictionary
    if not isinstance(query, dict) :
        return False

    # every key is allowed
    for key in query :
        if key not in allowed_keys :
            return False

    # flight_id and origin and destination must be text
    for key in string_keys :
        if key in query and not isinstance(query[key], str) :
            return False

    # departure_datetime and arrival_datetime must be text
    for key in datetime_keys :
        if key in query :
            if not isinstance(query[key], str) :
                return False
            if _parse_datetime(query[key]) is None :
                return False

    # price and min_price must be numbers
    for key in number_keys :
        if key in query and not _is_number(query[key]) :
            return False

    # sort_by must be one of the 6 keys of a flight
    if "sort_by" in query :
        if not isinstance(query["sort_by"], str) :
            return False
        if query["sort_by"] not in record_keys :
            return False

    # order must be "asc" or "desc", and it needs sort_by
    if "order" in query :
        if query["order"] not in ("asc", "desc") :
            return False
        if "sort_by" not in query :
            return False

    # limit must be whole number
    if "limit" in query :
        if isinstance(query["limit"], bool) or not isinstance(query["limit"], int) : 
            return False
        if query["limit"] < 0 :
            return False

    return True


def _flight_matches(flight : dict, query : dict) -> bool :
    """ if the flight respects all the conditions then it's true """

    # same text in the query
    for key in string_keys :
        if key in query and flight[key] != query[key] :
            return False

    # the flight leaves at this time or later
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"] :
        return False

    # the flight arrives at this time or earlier
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"] :
        return False

    # the price is lower or equal to the value
    if "price" in query and flight["price"] > query["price"] :
        return False

    # the price is higher or equal to this value
    if "min_price" in query and flight["price"] < query["min_price"] :
        return False

    # every conditions are respected
    return True


def run_query(db : list[dict], query : dict) -> dict :
    """one query is run and the results are returned """

    # bad query : we return an error
    if not _is_valid_query(query) :
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # keep only the flights that respect the conditions
    matches = []
    for flight in db :
        if _flight_matches(flight, query) :
            matches.append(dict(flight))   # we copy the flight

    # sort the flights if sort_by is given
    if "sort_by" in query :
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"
        matches = sorted(matches, key = lambda flight : flight[sort_key], reverse = descending)

    # keep only the first flights if limit is given
    if "limit" in query :
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db : list[dict], queries : dict | list) -> list[dict] :
    """ one or a list of query is runned we always return a list of result """


    # one query becomes a list with only one query
    if isinstance(queries, dict) :
        queries = [queries]

    # we run each query and keep the results in the same order
    results = []
    for query in queries :
        results.append(run_query(db, query))

    return results