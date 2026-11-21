""" this file reads the flight in the CSV file and it validates each row """


# ressources used for this file :
    # handle csv in python : https://www.youtube.com/watch?v=QhK0UadpeBo
    # errors report : https://www.youtube.com/watch?v=mD8hQrvfB6Y
    # dictionary in python : https://www.youtube.com/watch?v=a10AeJ_o-44&t=443s
    # os library : https://www.youtube.com/watch?v=EReeJSaU0Og
    




import csv    # it splits a line into fields
import os    

from validator import validate_row, to_record  # we take the file from validator and we import the 2 fonctions


def parse_files(paths : list[str], airports : set[str]) -> tuple[list[dict], list[str]] :
    """ this function reads the CSV files in order and return valid flights and error messages"""

    records = []    # valid flight records, in order
    errors = []       # error messages, in order
    seen_flights = set()    # flight_id, departure_datetime of valid rows already accepted

    # it processes the files in the order they were given
    for path in paths :

        # we keep only the file name not the folder
        # os.path.basename() gives the file name without the folder
        file_name = os.path.basename(path)
       
        # we open the file
        with open(path, encoding = "utf-8") as f :
       
            # we read the file line_number starts at 1
           
            for line_number, line in enumerate(f, start = 1) :
       
                # the first line is the header so we skip
                if line_number == 1 :
                    continue

                # we remove the line ending used when we copy the line into the log
                original_line = line.rstrip("\r\n")

                # we strip the line if its only whitespaces
                
                if original_line.strip() == "" :
                    continue

                # we skip the line if its a comment so begins with #
                if original_line.strip().startswith("#") :
                    continue

                # split the line into fields with the csv module
                
                fields = next(csv.reader([original_line]))

                # check 1 to 11 with the function from validator 
                error_code = validate_row(fields, airports)

                if error_code is not None :
                    # invalid row : build the message and go to the next line
                    errors.append(f"{file_name}:{line_number}: {error_code} | {original_line}")
                    continue

                # if the row is valid : convert it to a record
                record = to_record(fields)

                # error 12 : DUPLICATE_FLIGHT with the same flight_id and same departure_datetime
                
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen_flights :
                    errors.append(f"{file_name}:{line_number}: DUPLICATE_FLIGHT | {original_line}")
                    continue

                # if not a duplicate : remember it and keep the record
                seen_flights.add(key)
                records.append(record)

    return records, errors 