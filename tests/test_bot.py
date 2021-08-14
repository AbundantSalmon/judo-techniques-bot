import unittest

from src.bot import Bot


class UnitTestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(None)

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


if __name__ == "__main__":
    unittest.main()
