import pickle
import unittest

from src.bot import Bot


class Author:
    def __init__(self, name="test"):
        self.name = name


class FakeComment:  # TODO: Make a fake comment factory
    def __init__(self, body, author_name="test"):
        self.author = Author(author_name)
        self.body = body
        self.permalink = "http://google.com"


class UnitTestBot(unittest.TestCase):
    def setUp(self):
        # Load test data (deserialize)
        with open("tests/techniques_test_data.pickle", "rb") as handle:
            techniques_data = pickle.load(handle)
        self.bot = Bot(techniques_data)

    def test_hyphen_variation(self):
        expected = {
            "A-B-C-D",
            "A B-C-D",
            "A-B C-D",
            "A B C D",
            "A-B C D",
            "A B-C D",
            "A-B-C D",
            "A B C-D",
        }
        result = self.bot._generate_permutations_of_hyphen_variation("A B C D")
        self.assertCountEqual(result, expected)

    def test_permutation_of_space_separated_words(self):
        expected = {
            "A BC D",
            "A BCD",
            "ABCD",
            "AB C D",
            "A B CD",
            "ABC D",
            "A B C D",
            "AB CD",
        }
        result = self.bot._generate_permutations_of_space_separated_words("A B C D")
        self.assertCountEqual(result, expected)

    def test_get_mentioned_techniques_from_comment(self):
        comment = FakeComment(
            "I Uchi Mata that guy last week, but that was only after he Seoi Nage'd me"
        )

        techniques = self.bot._get_mentioned_techniques_from_comment(comment)

        self.assertEqual(len(techniques), 2)
        self.assertEqual(techniques[0].technique, "Seoi Nage")
        self.assertEqual(techniques[1].technique, "Uchi Mata")

    def test_get_no_mentioned_techniques_from_comment(self):
        comment = FakeComment(
            "I punched that guy last week, but that was only after he kicked me"
        )

        techniques = self.bot._get_mentioned_techniques_from_comment(comment)

        self.assertEqual(len(techniques), 0)


if __name__ == "__main__":
    unittest.main()
