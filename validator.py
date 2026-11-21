"""the code in this file validate flight rows"""


import math  # imports the math library
import re   # regular expressions for strict format checks
from datetime import datetime    # it checks that a date really exists


# defines the rules of format that the sentences must respect
# regex means regular expression

# ressource used for this file :
    
# explanation on regex : https://www.youtube.com/watch?v=UQQsYXa1EHs
# method on how to open files in python : https://www.youtube.com/watch?v=KGw7ppL1ntc
# error gestion : https://www.youtube.com/watch?v=sNJYSPNJIAc


    
# -------those lines are AI generated ----------------------------------

flight_id_re = re.compile(r"[A-Za-z0-9]{2,8}")   # we accept only the flight_id with 2 to 8 characters and that are ASCII or numbers 

airport_re = re.compile(r"[A-Z]{3}")   # for the airport code we accept exactly 3 uppercase ASCII letters

datetime_re = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")
# for the datetime we accept only this format : "YYYY-MM-DD HH:MM" we translate this in code

datetime_format = "%Y-%m-%d %H:%M"  # same format string but understood by strptime

# ----------------------------------------------------------------------


def load_airports(path : str) -> set[str] :
    """ the goal of this function is to read an airport list file and return the codes"""
    
    airports = set()     # it starts with an empty set of codes
    with open(path, encoding="utf-8") as f:   # opens the file as UTF-8 text
        for line in f:          # it reads the file one line at a time
            code = line.strip()   # remove spaces, tabs and the newline around the code 
            if not code or code.startswith("#"):  # this line skips blank lines and comment lines
                continue    # goes straight to the next line
            airports.add(code)    # keep the code exactly as written
    return airports


def _parse_datetime(text : str) -> datetime | None :
    """ this function returns the datetime if it matches this format : 'YYYY-MM-DD HH:MM' """
    
    if not datetime_re.fullmatch(text) :   # if the format doesn't match
        return None    # then we return nothing
    
    try :
        return datetime.strptime(text, datetime_format)  # checks if the date really exists
    except ValueError :   # it controls errors like month 13 for example
        return None    # we return nothing


def _is_valid_airport(code : str, airports : set[str]) -> bool :
    """ this function returns true if the airport has 3 uppercase ASCII letters and is in the list, it returns false otherwise """

    match = airport_re.fullmatch(code)    # it compares the whole string with the pattern [A-Z]{3}

    if match is None :   # if there is no match, we return false
        return False

    if code not in airports :  # now we check that the code is in the list
        return False

    return True   # if both checks are passed we return true


def validate_row(fields : list[str], airports : set[str]) -> str | None :
    """ this functions returns none if the row is valid """
    
    """Return None if the row is valid, else the error code of the first failing check."""
    
    
    # 1  WRONG_FIELD_COUNT : the row does not have exactly 6 fields.
    
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    # we clean the raw value
    
    flight_id = fields[0].strip()
    origin = fields[1].strip()
    destination = fields[2].strip()
    departure = fields[3].strip()
    arrival = fields[4].strip()
    price = fields[5].strip()
    
    
    # 2  MISSING_FIELD : after stripping, no field can be empty
     
    if not all((flight_id, origin, destination, departure, arrival, price)) :
        return "MISSING_FIELD"     # all() is false if a string is empty

    # 3  INVALID_FLIGHT_ID : it must be 2-8 ASCII letters
    
    if not flight_id_re.fullmatch(flight_id) :
        return "INVALID_FLIGHT_ID"

    # 4  INVALID_ORIGIN : it must be 3 uppercase ASCII letters and in the airport list
    
    if not _is_valid_airport(origin, airports) :
        return "INVALID_ORIGIN"
    
    # 5  INVALID_DESTINATION : same for destination
    if not _is_valid_airport(destination, airports) :
        return "INVALID_DESTINATION"

    # 6  SAME_ORIGIN_DESTINATION : a flight need to start and end at two different aiport
    if origin == destination :
        return "SAME_ORIGIN_DESTINATION"

    # 7  INVALID_DEPARTURE : none means bad format or fake date
    
    departure_dt = _parse_datetime(departure)
    if departure_dt is None :
        return "INVALID_DEPARTURE"
    
    # 8  INVALID_ARRIVAL : same for arrival
    
    arrival_dt = _parse_datetime(arrival)
    if arrival_dt is None :
        return "INVALID_ARRIVAL"

    # 9  ARRIVAL_NOT_AFTER_DEPARTURE : the arrival must be later than departure
    if arrival_dt <= departure_dt :            
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10  INVALID_PRICE : the price must be convertible by float() and be a finite number
    
    try :
        price_value = float(price)
    except ValueError :
        return "INVALID_PRICE"
    if not math.isfinite(price_value) :
        return "INVALID_PRICE"

    # 11  NON_POSITIVE_PRICE : the price must be bigger than zero
    if price_value <= 0 :
        return "NON_POSITIVE_PRICE"

    return None    # if everything passes 


def to_record(fields : list[str]) -> dict :
    """this function converts a valid row into a flight record dictionary"""
    
    # Same unpacking and stripping as in validate_row.
    flight_id, origin, destination, departure, arrival, price = (field.strip() for field in fields)
    return {
        "flight_id": flight_id,               
        "origin": origin,                    
        "destination": destination,        
        "departure_datetime": departure,      
        "arrival_datetime": arrival,         
        "price": float(price),
        
        }