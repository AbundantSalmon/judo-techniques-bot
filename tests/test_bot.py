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

        def test_build_technique_pattern_matches_all_variants(self):
            pattern = Bot._build_technique_pattern("o uchi gari")
            self.assertIsNotNone(pattern.search("o uchi gari"))
            self.assertIsNotNone(pattern.search("o-uchi-gari"))
            self.assertIsNotNone(pattern.search("ouchigari"))
            self.assertIsNotNone(pattern.search("o-uchi gari"))
            self.assertIsNotNone(pattern.search("o uchi-gari"))
            self.assertIsNone(pattern.search("o  uchi gari"))

        def test_build_technique_pattern_single_word(self):
            pattern = Bot._build_technique_pattern("judo")
            self.assertIsNotNone(pattern.search("judo"))
            self.assertIsNone(pattern.search("karate"))

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
                    1,
                    "throw",
                    ["english_names"],
                    "youtube_link",
                    "comment_url",
                    "author",
                    "technique_name_variant",
                ),
                MentionedTechnique(
                    2,
                    "throw_2",
                    ["english_names"],
                    "youtube_link",
                    "comment_url",
                    "author",
                    "technique_name_variant",
                ),
                MentionedTechnique(
                    1,
                    "throw",
                    ["english_names"],
                    "youtube_link",
                    "comment_url",
                    "author",
                    "technique_name_variant",
                ),
                MentionedTechnique(
                    1,
                    "throw",
                    ["english_names"],
                    "youtube_link",
                    "comment_url",
                    "author",
                    "technique_name_variant",
                ),
            ]

            techniques = self.bot._set_no_post_duplicates(test_values)

            self.assertEqual(techniques[0].will_be_posted, True)
            self.assertEqual(techniques[1].will_be_posted, True)
            self.assertEqual(techniques[2].will_be_posted, False)
            self.assertEqual(techniques[3].will_be_posted, False)

        def _make_comment_with_submission(self, existing_comments):
            """Helper to create a mock comment whose submission contains existing_comments."""
            comment = mock.MagicMock()
            comment.submission.comments.replace_more = mock.MagicMock()
            comment.submission.comments.list.return_value = existing_comments
            return comment

        def test_set_no_post_previously_translated_blocks_already_translated(self):
            bot_comment = mock.MagicMock()
            bot_comment.author.name = ""  # matches REDDIT_USERNAME in test env
            bot_comment.body = "Uchi Mata translation"

            comment = self._make_comment_with_submission([bot_comment])

            techniques = [
                MentionedTechnique(
                    1,
                    "Uchi Mata",
                    ["Inner Thigh Throw"],
                    "url",
                    "url",
                    "author",
                    "uchi mata",
                ),
            ]

            result = self.bot._set_no_post_previously_translated(comment, techniques)

            self.assertFalse(result[0].will_be_posted)

        def test_set_no_post_previously_translated_allows_new_technique(self):
            bot_comment = mock.MagicMock()
            bot_comment.author.name = ""  # matches REDDIT_USERNAME
            bot_comment.body = "Uchi Mata translation"

            comment = self._make_comment_with_submission([bot_comment])

            techniques = [
                MentionedTechnique(
                    2,
                    "Seoi Nage",
                    ["Shoulder Throw"],
                    "url",
                    "url",
                    "author",
                    "seoi nage",
                ),
            ]

            result = self.bot._set_no_post_previously_translated(comment, techniques)

            self.assertTrue(result[0].will_be_posted)

        def test_set_no_post_previously_translated_no_bot_comments(self):
            user_comment = mock.MagicMock()
            user_comment.author.name = "some_user"
            user_comment.body = "Uchi Mata is cool"

            comment = self._make_comment_with_submission([user_comment])

            techniques = [
                MentionedTechnique(
                    1,
                    "Uchi Mata",
                    ["Inner Thigh Throw"],
                    "url",
                    "url",
                    "author",
                    "uchi mata",
                ),
            ]

            result = self.bot._set_no_post_previously_translated(comment, techniques)

            self.assertTrue(result[0].will_be_posted)

        def test_set_no_post_previously_translated_skips_already_flagged(self):
            """Techniques already flagged will_be_posted=False should not trigger API fetch."""
            comment = mock.MagicMock()

            technique = MentionedTechnique(
                1,
                "Uchi Mata",
                ["Inner Thigh Throw"],
                "url",
                "url",
                "author",
                "uchi mata",
            )
            technique.will_be_posted = False

            result = self.bot._set_no_post_previously_translated(comment, [technique])

            self.assertFalse(result[0].will_be_posted)
            # submission.comments should never be accessed
            comment.submission.comments.replace_more.assert_not_called()

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
            comment.reply.side_effect = praw.exceptions.APIException(  # ty:ignore[possibly-missing-submodule]
                ["test", "test", "test"]
            )

            techniques_to_translate = []

            self.bot._reply_to_comment(comment, techniques_to_translate)

            self.assertEqual(comment.reply.call_count, 4)

        def test_non_retry_for_replying_to_comments(self):
            comment = mock.MagicMock()
            comment.reply.side_effect = [
                praw.exceptions.APIException(["test", "test", "test"]),  # ty:ignore[possibly-missing-submodule]
                None,
            ]

            techniques_to_translate = []

            self.bot._reply_to_comment(comment, techniques_to_translate)

            self.assertEqual(comment.reply.call_count, 2)

    if __name__ == "__main__":
        unittest.main()
