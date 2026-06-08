import dataclasses
import logging
import re
from time import sleep
from typing import List

import praw
from .config import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDDIT_PASSWORD,
    REDDIT_USERNAME,
    SUBREDDITS,
    USER_AGENT,
    VERSION,
)
from .db import session_scope
from .models import DetectedJudoTechniqueMentionEvent, CachedTechniques

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MentionedTechnique:
    technique_id: int
    technique: str
    english_names: list[str]
    youtube_link: str
    comment_url: str
    author: str
    technique_name_variant: str
    will_be_posted: bool = True


class Bot:
    MAX_RETRIES = 3

    def __init__(
        self, data: dict[str, CachedTechniques], time_between_retry: int = 10 * 60
    ) -> None:
        self.data: dict[str, CachedTechniques] = data
        self._technique_patterns: dict[str, re.Pattern] = {
            name: self._build_technique_pattern(name.lower()) for name in data.keys()
        }
        self.time_between_retry = time_between_retry

    def run(self):
        logger.info("Bot starting...")
        logger.info("Version: " + VERSION)

        stream = self._initialize()

        logger.info("Reading comments...")
        for comment in stream.comments(skip_existing=True):
            if comment.author is None:
                # For some unknown reason, comments can have no authors, skip these
                continue
            if comment.author.name == REDDIT_USERNAME:
                # Skips bot's own comment
                continue
            logger.info(
                "Username: " + comment.author.name + " Message:\t" + comment.body
            )

            mentioned_techniques = self._get_mentioned_techniques_from_comment(comment)
            mentioned_techniques = self._set_no_post_duplicates(mentioned_techniques)
            mentioned_techniques = self._set_no_post_previously_translated(
                comment, mentioned_techniques
            )
            self._save_records(mentioned_techniques)
            techniques_to_translate = self._filter_for_translations(
                mentioned_techniques
            )
            logger.info(
                "Detected judo techniques in comment:",
            )
            logger.info(
                [technique.technique_name_variant for technique in mentioned_techniques]
            )

            if len(techniques_to_translate) != 0:
                logger.info(
                    "Providing translations for:",
                )
                logger.info(
                    [
                        technique.technique_name_variant
                        for technique in techniques_to_translate
                    ]
                )
                self._reply_to_comment(comment, techniques_to_translate)
            else:
                # do nothing
                logger.info(
                    "No judo techniques translated from the comment\n_____________________"
                )

    def _initialize(self):
        logger.info(f"Bot connecting to subreddits: {SUBREDDITS}...")
        reddit = praw.Reddit(
            user_agent=USER_AGENT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
        )

        logger.info("Bot connection to reddit done!")
        return reddit.subreddit(SUBREDDITS).stream

    def _get_mentioned_techniques_from_comment(
        self, comment
    ) -> List[MentionedTechnique]:
        """
        Determines whether the supplied comment has a judo technique,
        returns with a list of the ids of any found judo techniques.
        Empty list is no judo techniques found.
        """
        mentioned_techniques: list[MentionedTechnique] = []

        original_author = comment.author.name
        if original_author == REDDIT_USERNAME:
            # Do not process if the bot has read it's own comment
            return mentioned_techniques
        comment_body_lower_case = comment.body.lower()
        for japanese_name in self.data.keys():
            technique_id = self.data[japanese_name]["id"]
            pattern = self._technique_patterns[japanese_name]
            for match in pattern.finditer(comment_body_lower_case):
                mentioned_techniques.append(
                    MentionedTechnique(
                        technique_id,
                        japanese_name,
                        self.data[japanese_name]["english_names"],
                        self.data[japanese_name]["video_url"],
                        comment.permalink,
                        original_author,
                        technique_name_variant=match.group(),
                    )
                )
        return mentioned_techniques

    def _set_no_post_duplicates(self, mentioned_techniques: List[MentionedTechnique]):
        """
        Set flag `will_be_posted` for all duplicated techniques to False
        """
        techniques = []
        for mentioned_technique in mentioned_techniques:
            if mentioned_technique.technique not in techniques:
                techniques.append(mentioned_technique.technique)
            else:
                mentioned_technique.will_be_posted = False
        return mentioned_techniques

    def _set_no_post_previously_translated(
        self,
        comment,
        mentioned_techniques: List[MentionedTechnique],
    ):
        """
        This function will check to see whether the techniques have been
        previously translated and prevent further translations
        """
        cached_comment_bodies = None
        for mentioned_technique in mentioned_techniques:
            if mentioned_technique.will_be_posted is not False:
                if cached_comment_bodies is None:
                    # cache the comment bodies of the post
                    parent_submission = comment.submission.comments
                    parent_submission.replace_more(limit=None)
                    cached_comment_bodies = [
                        c.body
                        for c in parent_submission.list()
                        if c.author is not None and c.author.name == REDDIT_USERNAME
                    ]
                for body in cached_comment_bodies:
                    if mentioned_technique.technique in body:
                        mentioned_technique.will_be_posted = False
                        break
        return mentioned_techniques

    def _save_records(self, mentioned_techniques: List[MentionedTechnique]):
        """
        Save DetectedJudoTechniqueMentionEvent to the DB
        """
        with session_scope() as s:
            for technique in mentioned_techniques:
                s.add(
                    DetectedJudoTechniqueMentionEvent(
                        technique_id=technique.technique_id,
                        name_variant=technique.technique_name_variant,
                        author=technique.author,
                        comment_url=technique.comment_url,
                        translated=technique.will_be_posted,
                    )
                )

    def _filter_for_translations(self, mentioned_techniques: List[MentionedTechnique]):
        return [
            technique for technique in mentioned_techniques if technique.will_be_posted
        ]

    def _reply_to_comment(
        self, comment, techniques_to_translate: List[MentionedTechnique]
    ):
        # code to reply to comment here, need to figureout what argument are req
        text = (
            "The Japanese terms mentioned in the above comment were: \n\n\n"
            + "|Japanese|English|Video Link| \n"
            + "|---|---|---|\n"
        )
        for tech in techniques_to_translate:
            for index, english_name in enumerate(tech.english_names):
                japanese_name = tech.technique if index == 0 else ""
                youtube_link = tech.youtube_link if index == 0 else ""
                youtube_string = (
                    " " if youtube_link is None else "[here](" + youtube_link + ")"
                )
                tech_text = (
                    f"|**{japanese_name}**: | *{english_name}* | {youtube_string}|\n"
                    if index == 0
                    else f"||*{english_name}* ||\n"
                )
                text += tech_text
        text += (
            "\n\nAny missed names may have already been translated in my "
            + "previous comments in the post."
            + "\n\n______________________\n\n"
            + f"^(Judo Techniques Bot: v{VERSION}.)"
            " ^(See my) [^(code)](https://github.com/AbundantSalmon/judo-techniques-bot). ^(See my) [^(stats)](https://judo-techniques-bot-stats.vercel.app/)\n\n"
        )
        try:
            comment.reply(text)
        except praw.exceptions.APIException as e:  # ty:ignore[possibly-missing-submodule]
            logger.exception(e)
            EXCEPTION_ERRORS = [
                "DELETED_COMMENT",
                "COMMENT_UNREPLIABLE",
                "SOMETHING_IS_BROKEN",
            ]
            if e.error_type in EXCEPTION_ERRORS:
                logger.info(
                    f"Comment that was being replied to was found to be {e.error_type}, no reply made."
                )
            else:
                for _ in range(self.MAX_RETRIES):
                    try:
                        logger.exception(
                            e
                        )  # Capture exception to understand what is happening
                        logger.warning("Sleeping 10 min, then retry")
                        sleep(self.time_between_retry)
                        logger.warning("Retrying")
                        comment.reply(text)
                        break
                    except praw.exceptions.APIException as inner_e:  # ty:ignore[possibly-missing-submodule]
                        if inner_e.error_type in EXCEPTION_ERRORS:
                            logger.info(
                                f"Comment that was being replied to was found to be {inner_e.error_type}, no reply made."
                            )
                            break

        logger.info("Replied!\n_____________________")

    @staticmethod
    def _build_technique_pattern(japanese_name_lower: str) -> re.Pattern:
        """
        Build a regex that matches all space/hyphen/concatenated variants of a technique name.
        e.g. "o uchi gari" -> r"o[ \\-]?uchi[ \\-]?gari"
        Matches: "o uchi gari", "o-uchi-gari", "ouchigari", "o-uchi gari", etc.
        """
        words = japanese_name_lower.split(" ")
        pattern = "[ \\-]?".join(re.escape(word) for word in words)
        return re.compile(pattern)
