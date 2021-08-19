from datetime import datetime, timezone
from itertools import product
from time import sleep
from typing import List, Set

import praw
from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDDIT_PASSWORD,
    REDDIT_USERNAME,
    SUBREDDITS,
    USER_AGENT,
    VERSION,
)
from db import session_scope
from models import DetectedJudoTechniqueMentionEvent


class MentionedTechnique:
    """
    Data class struct
    """

    def __init__(
        self,
        technique_id,
        technique,
        english_names,
        youtube_link,
        comment_url,
        author,
        technique_name_variant=None,
    ):
        self.technique = technique
        self.technique_id = technique_id
        self.technique_name_variant = (
            technique if technique_name_variant is None else technique_name_variant
        )
        self.english_names = english_names
        self.youtube_link = youtube_link
        self.comment_url = comment_url
        self.author = author
        self.will_be_posted = True


class Bot:
    def __init__(self, data) -> None:
        self.data = data

    def run(self):
        print("Bot Started")

        stream = self._initialize()

        print("Reading comments...")
        for comment in (
            comment
            for comment in stream.comments(skip_existing=True)
            if comment.author.name != REDDIT_USERNAME
        ):  # Skips bot's own comment
            print("\t" + comment.body)

            mentioned_techniques = self._get_mentioned_techniques_from_comment(comment)
            mentioned_techniques = self._set_no_post_duplicates(mentioned_techniques)
            mentioned_techniques = self._set_no_post_previously_translated(
                comment, mentioned_techniques
            )
            self._save_records(mentioned_techniques)
            techniques_to_translate = self._filter_for_translations(
                mentioned_techniques
            )

            if len(techniques_to_translate) != 0:
                print("Detected judo techniques in comment:\n\t", end="")
                print(
                    [
                        technique.technique_name_variant
                        for technique in mentioned_techniques
                    ]
                )
                print("Providing translations for:\n\t", end="")
                print(
                    [
                        technique.technique_name_variant
                        for technique in techniques_to_translate
                    ]
                )
                self._reply_to_comment(comment, techniques_to_translate)
            else:
                # do nothing
                print(
                    "No judo techniques translated from the comment\n_____________________"
                )

    def _initialize(self):
        print("Initializing")
        reddit = praw.Reddit(
            user_agent=USER_AGENT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
        )

        print("Initialisation Done")
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
        for japanese_name in self.data.keys():
            japanese_name_lower_case = japanese_name.lower()
            comment_body_lower_case = comment.body.lower()
            technique_id = self.data[japanese_name]["id"]
            set_of_combinations = self._generate_permutations_of_space_separated_words(
                japanese_name_lower_case
            )

            # TODO: Would it be better to generate and hold list of all combinations in memory?
            for phrase in set_of_combinations:
                indices_of_mentions = list(
                    self._find_all(comment_body_lower_case, phrase)
                )
                if len(indices_of_mentions) > 0:  # TODO: replace with regex
                    for x in indices_of_mentions:
                        mentioned_techniques.append(
                            MentionedTechnique(
                                technique_id,
                                japanese_name,
                                self.data[japanese_name]["english_names"],
                                self.data[japanese_name]["video_url"],
                                comment.permalink,
                                original_author,
                                technique_name_variant=phrase,
                            )
                        )
                for (
                    hyphenated_phrase
                ) in self._generate_permutations_of_hyphen_variation(phrase):
                    indices_of_hyphen_mentions = list(
                        self._find_all(comment_body_lower_case, hyphenated_phrase)
                    )
                    if len(indices_of_hyphen_mentions) > 0:  # TODO: replace with regex
                        for x in indices_of_hyphen_mentions:
                            mentioned_techniques.append(
                                MentionedTechnique(
                                    technique_id,
                                    japanese_name,
                                    self.data[japanese_name]["english_names"],
                                    self.data[japanese_name]["video_url"],
                                    comment.permalink,
                                    original_author,
                                    technique_name_variant=hyphenated_phrase,
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
        for mentioned_technique in mentioned_techniques:
            if mentioned_technique.will_be_posted is not False:
                parent_submission = comment.submission.comments
                parent_submission.replace_more(limit=None)
                for comment in parent_submission.list():
                    if (
                        comment.author is not None
                        and comment.author.name == REDDIT_USERNAME
                        and mentioned_technique.technique in comment.body
                    ):
                        mentioned_technique.will_be_posted = False
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
            f"\n\nAny missed names may have already been translated in my "
            + "previous comments in the post."
            + "\n\n______________________\n\n"
            + f"Judo Bot {VERSION}: If you have any comments or suggestions "
            + "please don't hesitate to direct message "
            + "[me](https://reddit.com/message/compose/?to=JudoTechniquesBot).\n\n"
        )
        try:
            comment.reply(text)
        except praw.exceptions.APIException as e:
            print(e)
            if e.error_type == "DELETED_COMMENT":
                print(
                    "Comment that was being replied to was found to be deleted, no reply made."
                )
            else:
                print(
                    "Sleeping 10 min, then retry"
                )  # TODO: Think of a better way to handle
                sleep(10 * 60)
                # retry posting after 10 minutes
                self._reply_to_comment(comment, techniques_to_translate)

        print("Replied!\n_____________________")
        return

    def _generate_permutations_of_space_separated_words(self, phrase: str) -> Set[str]:
        """
        Set of permutations of all the possible permutations of space removal
        e.g. O uchi gari -> Ouchigari, O uchigari, Ouchi gari
        Works recursively
        """
        list_of_words = phrase.split(" ")
        if len(list_of_words) == 1:
            return list_of_words

        set_of_phrases = set()

        for index, word in enumerate(list_of_words):
            if index is not len(list_of_words) - 1:
                new_phrase = (
                    " ".join(list_of_words[:index])
                    + " "
                    + word
                    + list_of_words[index + 1]
                    + " "
                    + " ".join(list_of_words[index + 2 :])
                ).strip()
                set_of_phrases.update(
                    self._generate_permutations_of_space_separated_words(new_phrase)
                )

        set_of_phrases.update([phrase])
        return set_of_phrases

    def _generate_permutations_of_hyphen_variation(self, phrase: str) -> Set[str]:
        """
        Returns a set of all permutations of when a ' ' is replaced by a '-'
        e.g. O uchi gari -> O-uchi gari, O uchi-gari O-uchi-gari
        A B C D -> A-B C D, A B-C D, A B C-D, A-B-C D, A-B C-D, A B-C-D, A-B-C-D
        """
        number_of_spaces = phrase.count(" ")
        index_of_all_spaces = list(self._find_all(phrase, " "))
        set_of_all_hyphen_variations = set()
        for x in product(range(2), repeat=number_of_spaces):
            hyphenated_phrase = phrase
            for count, change_to_hyphen in enumerate(x):
                if change_to_hyphen == 1:
                    list_of_characters = list(hyphenated_phrase)
                    list_of_characters[index_of_all_spaces[count]] = "-"
                    hyphenated_phrase = "".join(list_of_characters)
            set_of_all_hyphen_variations.add(hyphenated_phrase)
        set_of_all_hyphen_variations.discard(phrase)  # remove original phrase
        return set_of_all_hyphen_variations

    def _find_all(self, string, substring):
        """
        Generator of indices to all the starting index of a substring in the string
        """
        start_index = 0
        while True:
            start_index = string.find(substring, start_index)
            if start_index == -1:
                return
            yield start_index
            start_index += len(
                substring
            )  # can use start += 1 to find overlapping matches
