import pickle
import praw
import unittest
from unittest import mock

with (
    mock.patch.dict(
        "os.environ",
        {
            "USER_AGENT": "",
            "CLIENT_ID": "",
            "CLIENT_SECRET": "",
            "REDDIT_USERNAME": "",
            "REDDIT_PASSWORD": "",
            "SUBREDDITS": "",
            "SENTRY_DSN": "",
            "DB_NAME": "",
            "DB_USER": "",
            "DB_PASS": "",
            "DB_HOST": "",
            "DB_PORT": "",
        },
    ),
    mock.patch("sqlalchemy.create_engine"),
):
    from judo_techniques_bot.bot import Bot, MentionedTechnique

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
            self.bot = Bot(techniques_data, time_between_retry=0)

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

        def test_generate_permutations_of_hyphen_variation(self):
            expected = {
                "A-B C D",
                "A B-C D",
                "A B C-D",
                "A-B-C D",
                "A-B C-D",
                "A B-C-D",
                "A-B-C-D",
            }
            result = self.bot._generate_permutations_of_hyphen_variation("A B C D")
            self.assertCountEqual(result, expected)

        def test_find_all(self):
            expected = [0, 15, 31]
            result = list(
                self.bot._find_all(
                    "hello my baby, hello my honey, hello my old time gal", "hello"
                )
            )
            self.assertCountEqual(result, expected)

        def test_get_mentioned_techniques_from_comment(self):
            comment = FakeComment(
                "I Uchi Mata that guy last week, but that was only after he seoi Nage'd me"
            )

            techniques = self.bot._get_mentioned_techniques_from_comment(comment)

            self.assertEqual(len(techniques), 2)
            self.assertEqual(techniques[0].technique, "Seoi Nage")
            self.assertEqual(techniques[1].technique, "Uchi Mata")

        def test_get_mentioned_techniques_from_comment_repeated(self):
            comment = FakeComment(
                "I Uchi Mata that guy last week, but that was only after he seoi "
                "Nage'd me. I will seoi-nage him next time."
            )

            techniques = self.bot._get_mentioned_techniques_from_comment(comment)

            self.assertEqual(len(techniques), 3)
            self.assertEqual(techniques[0].technique, "Seoi Nage")
            self.assertEqual(techniques[0].technique_name_variant, "seoi nage")
            self.assertEqual(techniques[1].technique, "Seoi Nage")
            self.assertEqual(techniques[1].technique_name_variant, "seoi-nage")
            self.assertEqual(techniques[2].technique, "Uchi Mata")

        def test_set_no_post_duplicates(self):
            test_values = [
                MentionedTechnique(
                    "1",
                    "throw",
                    "english_names",
                    "youtube_link",
                    "comment_url",
                    "author",
                ),
                MentionedTechnique(
                    "2",
                    "throw_2",
                    "english_names",
                    "youtube_link",
                    "comment_url",
                    "author",
                ),
                MentionedTechnique(
                    "1",
                    "throw",
                    "english_names",
                    "youtube_link",
                    "comment_url",
                    "author",
                ),
                MentionedTechnique(
                    "1",
                    "throw",
                    "english_names",
                    "youtube_link",
                    "comment_url",
                    "author",
                ),
            ]

            techniques = self.bot._set_no_post_duplicates(test_values)

            self.assertEqual(techniques[0].will_be_posted, True)
            self.assertEqual(techniques[1].will_be_posted, True)
            self.assertEqual(techniques[2].will_be_posted, False)
            self.assertEqual(techniques[3].will_be_posted, False)

        def test_get_no_mentioned_techniques_from_comment(self):
            comment = FakeComment(
                "I punched that guy last week, but that was only after he kicked me"
            )

            techniques = self.bot._get_mentioned_techniques_from_comment(comment)

            self.assertEqual(len(techniques), 0)

        def test_normal_replying_to_comments(self):
            comment = mock.MagicMock()

            techniques_to_translate = []

            self.bot._reply_to_comment(comment, techniques_to_translate)

            self.assertEqual(comment.reply.call_count, 1)

        def test_max_retry_for_replying_to_comments(self):
            comment = mock.MagicMock()
            comment.reply.side_effect = praw.exceptions.APIException(  # ty:ignore[possibly-missing-attribute]
                ["test", "test", "test"]
            )

            techniques_to_translate = []

            self.bot._reply_to_comment(comment, techniques_to_translate)

            self.assertEqual(comment.reply.call_count, 4)

        def test_non_retry_for_replying_to_comments(self):
            comment = mock.MagicMock()
            comment.reply.side_effect = [
                praw.exceptions.APIException(["test", "test", "test"]),  # ty:ignore[possibly-missing-attribute]
                None,
            ]

            techniques_to_translate = []

            self.bot._reply_to_comment(comment, techniques_to_translate)

            self.assertEqual(comment.reply.call_count, 2)

    if __name__ == "__main__":
        unittest.main()
