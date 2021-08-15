import pickle


def coerce_to_list(value) -> list:
    if isinstance(value, list):
        return value
    else:
        return [value]


def pickle_dictionary(dictionary, filename):
    # Store data (serialize)
    with open(f"{filename}.pickle", "wb") as handle:
        pickle.dump(dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
