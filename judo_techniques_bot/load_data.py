import csv
import os

TECHNIQUES_DATA_FILE = "data/techniques_fixtures.csv"

folder = os.path.dirname(os.path.abspath(__file__))
file_location = os.path.join(folder, TECHNIQUES_DATA_FILE)


def retrieve_fixture_data():
    print("Retrieving technique data from:")
    print(file_location)

    array_of_techniques = []

    with open(file_location, "r") as file:
        for row in csv.DictReader(file):
            japanese_names = row.pop("japanese_names")
            row["japanese_names"] = japanese_names.split(",")
            english_names = row.pop("english_names")
            row["english_names"] = english_names.split(",")
            array_of_techniques.append(row)

    return array_of_techniques
