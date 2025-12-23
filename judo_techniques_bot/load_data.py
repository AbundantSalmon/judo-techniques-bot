import csv
import os

from .db import session_scope
from .models import Technique

TECHNIQUES_DATA_FILE = "data/techniques_fixtures.csv"

folder = os.path.dirname(os.path.abspath(__file__))
file_location = os.path.join(folder, TECHNIQUES_DATA_FILE)


def retrieve_fixture_data():
    print("Retrieving technique data from:")
    print(file_location)

    array_of_techniques: list[Technique] = []
    with session_scope() as s:
        with open(file_location, "r") as file:
            for row in csv.DictReader(file):
                array_of_techniques.append(
                    Technique(
                        japanese_display_name=row["japanese_display_name"],
                        japanese_names=row["japanese_names"].split(","),
                        english_names=row["english_names"].split(","),
                        video_url=row["video_url"],
                    )
                )
        s.bulk_save_objects(array_of_techniques)

    print(f"{len(array_of_techniques)} technique(s) data loaded!")

    return array_of_techniques


if __name__ == "__main__":
    retrieve_fixture_data()
