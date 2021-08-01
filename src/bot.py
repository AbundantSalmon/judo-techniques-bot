import sqlite3
from datetime import datetime, timezone
from itertools import product

# from sqlite3 import Error
from time import sleep

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


class MentionedTechnique:
    """
    Data class struct
    """

    def __init__(self, technique_id, technique, comment_url):
        self.technique = technique
        self.technique_id = technique_id
        self.comment_url = comment_url
        self.will_be_posted = True


class Bot:
    def __init__(self, data) -> None:
        self.data = data

    def run(self):
        print("Bot Started")

        stream = self._initialize()

        print("Reading comments...")
        for comment in stream.comments(skip_existing=True):
            print("\t" + comment.body)

            mentioned_techniques = self._get_mentioned_techniques_from_comment(comment)
            mentioned_techniques = self._set_no_post_duplicates(mentioned_techniques)
            # mentioned_techniques = self.set_no_post_previously_translated(
            #     mentioned_techniques
            # )

            if len(mentioned_techniques) != 0:
                print(mentioned_techniques)
                # self.reply_to_comment(comment, mentioned_techniques)
            else:
                # do nothing
                print("No Judo comment\n_____________________")

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

    def _get_mentioned_techniques_from_comment(self, comment):
        """
        Determines whether the supplied comment has a judo technique,
        returns with a list of the ids of any found judo techniques.
        Empty list is no judo techniques found.
        """
        technique_ids = []

        original_author = comment.author.name
        if original_author == REDDIT_USERNAME:
            # Do not process if the bot has read it's own comment
            return technique_ids
        for japanese_name in self.data.keys():
            japanese_name_lower_case = japanese_name.lower()
            comment_body_lower_case = comment.body.lower()
            technique_id = self.data[japanese_name]["id"]
            list_of_combinations = self._space_removal_variation(
                japanese_name_lower_case
            )

            in_comments = False
            for combination in list_of_combinations:
                if (
                    combination.lower() in comment_body_lower_case
                ):  # TODO: replace with regex
                    in_comments = True
                for x in self._hythen_variation(combination):
                    if x in comment_body_lower_case:  # TODO: replace with regex
                        in_comments = True
            if in_comments == True:
                technique_ids.append(
                    MentionedTechnique(technique_id, japanese_name, comment.permalink)
                )
        return technique_ids

    def _set_no_post_duplicates(self, mentioned_techniques):
        """
        TODO: Set flag `will_be_posted` for all duplicated techniques to False
        """
        return mentioned_techniques

    def _set_no_post_previously_translated():
        """
        TODO: This function will check to see whether the techniques have been
        previously translated
        """

        # Remove techniques if judo techniques bot has already previously posted the meaning of the same techniques
        techniques_ids_unique = []
        for technique in technique_ids:

            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute(
                "UPDATE id SET mentionsNo = mentionsNo + 1 WHERE techniqueID=?",
                (technique,),
            )
            cur.execute(
                "INSERT INTO datalog (datetime,judotech,author,entrytype) VALUES(?,?,?,?)",
                (
                    datetime.now(timezone.utc),
                    technique,
                    original_author,
                    "mentionedincomments",
                ),
            )
            conn.commit()
            conn.close()

            in_comments = False
            parent_submission = comment.submission.comments
            parent_submission.replace_more(limit=None)
            for comment in parent_submission.list():
                if comment.author == None:
                    continue
                if comment.author.name == REDDIT_USERNAME:
                    japaneseName = self.select_japanesename(technique)[0][2]
                    if japaneseName in comment.body:
                        in_comments = True
            if in_comments == False:
                techniques_ids_unique.append(technique)
        return techniques_ids_unique

    def _reply_to_comment(self, comment, techniqueIDs):
        # code to reply to comment here, need to figureout what argument are req
        text = "The Japanese terms mentioned in the above comment were: \n\n\n|Japanese|English|Video Link| \n|---|---|---|\n"
        for tech in techniqueIDs:
            englishNames = self._select_englishname(tech)
            numberOfEnglishNames = len(englishNames)

            for x in range(0, numberOfEnglishNames):
                if x == 0:
                    japaneseName = self._select_japanesename(tech)[0][2]
                else:
                    japaneseName = ""
                englishName = self._select_englishname(tech)[x][0]
                if x == 0:
                    youtubeLink = self._select_youtubeLink(tech)[0][0]
                else:
                    youtubeLink = ""
                if youtubeLink is None:
                    youtubeString = " "
                else:
                    youtubeString = "[here](" + youtubeLink + ")"
                if japaneseName != "":
                    techText = (
                        "|**"
                        + japaneseName
                        + "**: | *"
                        + englishName
                        + "* | "
                        + youtubeString
                        + "|\n"
                    )
                else:
                    techText = "||*" + englishName + "* ||\n"
                text += techText
            print(text)
        text += (
            "\n\nAny missed names may have already been translated in my previous comments in the post.\n\n______________________\n\nJudo Bot "
            + VERSION
            + ": If you have any comments or suggestions please don't hesitate to direct message [me](https://reddit.com/message/compose/?to=JudoTechniquesBot).\n\n"
        )
        try:
            comment.reply(text)

            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute(
                "UPDATE id SET postsNo = postsNo + 1 WHERE techniqueID=?", (tech,)
            )
            cur.execute(
                "INSERT INTO datalog (datetime,judotech,author,entrytype) VALUES(?,?,?,?)",
                (
                    datetime.now(timezone.utc),
                    tech,
                    comment.author.name,
                    "judobotreply",
                ),
            )
            conn.commit()
            conn.close()
        except praw.exceptions.APIException as e:
            print(e)
            if e.error_type == "DELETED_COMMENT":
                print(
                    "Comment that was being replied to was found to be deleted, no reply made."
                )
            else:
                print("sleeping 10 min, then retry")
                sleep(10 * 60)
                # retry posting after 10 minutes
                self._reply_to_comment(comment, techniqueIDs)

        print("replying\n_____________________")
        return

    def _select_all_japanesenamestable(self):
        conn = sqlite3.connect(DATABASE)

        cur = conn.cursor()
        cur.execute("SELECT * FROM japanesenamestable")

        rows = cur.fetchall()

        conn.close()

        return rows

    def _select_englishname(self, techID):
        conn = sqlite3.connect(DATABASE)

        cur = conn.cursor()
        cur.execute("SELECT * FROM englishnamestable WHERE techniqueID = ?", (techID,))

        rows = cur.fetchall()

        conn.close()

        return rows

    def _select_japanesename(self, techID):
        conn = sqlite3.connect(DATABASE)

        cur = conn.cursor()
        cur.execute("SELECT * FROM japanesenamestable WHERE techniqueID = ?", (techID,))
        rows = cur.fetchall()

        conn.close()

        return rows

    def _select_youtubeLink(self, techID):
        conn = sqlite3.connect(DATABASE)

        cur = conn.cursor()
        cur.execute("SELECT youtubeLink FROM id WHERE techniqueID = ?", (techID,))
        rows = cur.fetchall()

        conn.close()

        return rows

    def _space_removal_variation(self, phrase):
        # space removal variation and removes duplicates
        listOfVariations = [phrase]
        listOfVariations += self._permutation_of_single_combination(phrase)
        listOfVariations = list(dict.fromkeys(listOfVariations))
        return listOfVariations

    def _permutation_of_single_combination(self, phrase):
        # permutation of all the possible permutations of space removal
        listOfParts = phrase.split(" ")
        numberOfParts = len(listOfParts)
        listOfPermutations = []
        if numberOfParts == 1:
            return []
        else:
            for x in range(0, numberOfParts - 1):
                permutationPhrase = ""
                for y in range(0, x):
                    permutationPhrase += listOfParts[y] + " "

                permutationPhrase += listOfParts[x] + listOfParts[x + 1] + " "

                for y in range(x + 2, numberOfParts):
                    permutationPhrase += listOfParts[y] + " "

                permutationPhrase = permutationPhrase.strip()
                listOfPermutations += [
                    permutationPhrase
                ] + self._permutation_of_single_combination(permutationPhrase)

        return listOfPermutations

    def _hythen_variation(self, phrase):
        # returns list of all permutations of when a ' ' is replaced by a '-'
        numberOfSpaces = phrase.count(" ")
        indexOfAllSpaces = list(self._find_all(phrase, " "))
        listOfHythenVariations = []
        for x in product(range(2), repeat=numberOfSpaces):
            tempPhrase = phrase
            for count, y in enumerate(x, 0):
                if y == 1:
                    l = list(tempPhrase)
                    l[indexOfAllSpaces[count]] = "-"
                    tempPhrase = "".join(l)
            listOfHythenVariations.append(tempPhrase)
        return listOfHythenVariations

    def _find_all(self, a_str, sub):
        # returns a list of indices to all the start index of a substring in the string
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1:
                return
            yield start
            start += len(sub)  # use start += 1 to find overlapping matches
