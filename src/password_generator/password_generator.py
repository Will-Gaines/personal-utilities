import logging
import pathlib as pl
import random as r
import typing as t

from src import constants as c

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)


class PasswordGenerator:
    """
    Object for generating local passwords, initially just from the dictionary file provided in this repo.
    Goals to build out:
    1. Configure the number of words in the password, and min/max length of words and the total password
    2. Add an option to make some common symbol substitutions
    3. Make it possible to provide a dictionary of keywords to use instead as an input
    4. Add a duckDb backend to both log common words for usage, and to store generated passwords
    """

    def __init__(self, dictionary_file_path: t.Optional[pl.Path] = None):
        self.alphanumeric_strings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.special_characters = "!@£$%&?"
        self.replacements = {
            "3": "£",
            "1": "!",
            "A": "@",
        }
        if dictionary_file_path is None:
            self.dictionary_file_path: pl.Path = (
                c.CONTENT_ROOT / "src" / "password_generator" / "word_file.txt"
            )
        else:
            self.dictionary_file_path = dictionary_file_path

        if not self.dictionary_file_path.exists():
            raise FileNotFoundError(
                f"Given dictionary path {self.dictionary_file_path} does not exist. Fix this, and try again"
            )

    def load_and_filter_library(
        self, min_word_length: int, max_word_length: int
    ) -> list[str]:
        """
        Load the word dictionary provided in class instantiation, and return all words with length between the
        min and max inputs (inclusive)
        :param min_word_length: Shortest word length to allow
        :param max_word_length: Longest word length to allow
        :return:
        """
        if max_word_length < min_word_length:
            raise ValueError(
                f"Max word length {max_word_length} can not be less than the minimum word length {min_word_length}"
            )

        # We validated the files existence at instantiation, so we proceed blindly here
        raw_list = self.dictionary_file_path.read_text().split("\n")
        return [
            word for word in raw_list if min_word_length <= len(word) <= max_word_length
        ]

    @staticmethod
    def pick_random_word(word_list: list[str]) -> str:
        """
        Given a list of words, returns one at random in title case
        :param word_list:
        :return:
        """
        return word_list.pop(r.randint(0, len(word_list))).title()

    def construct_password(
        self,
        word_list: list[str],
        min_password_length: int,
        max_password_length: int,
        separator: str = "",
    ) -> str:
        """
        Construct a password from the word list given, until it meets the minimum length criteria given. Distinct words
        are title case by default, and concatenated using the separator provided (empty by default)
        Once the minimum length is met, up to 3 attempts will be made to add additional words. If all 3 cases take it
        over the maximum length, no more will be added
        :param word_list:
        :param min_password_length:
        :param max_password_length:
        :param separator:
        :return:
        """
        # Get our first word, and use `pop` method to avoid duplicates
        password = self.pick_random_word(word_list=word_list)

        logger.debug(f"Word chosen from the list: {password}")
        logger.debug(f"Remaining word list: {word_list}")

        # First loop set to meet our minimum requirement
        while len(password) < min_password_length:
            new_word = separator + self.pick_random_word(word_list=word_list)
            logger.debug(f"Word chosen from the list: {new_word}")
            logger.debug(f"Remaining word list: {word_list}")

            if len(password + new_word) > max_password_length:
                continue
            password += new_word

        # Here, the password should be of minimal length, so we see if we can build on it, without going over
        # in 3 attempts
        attempt_counter = 0

        # Include `and word_list` condition so that if we exhaust the word list in our search, we exit too
        while attempt_counter < 3 and word_list:
            new_word = separator + self.pick_random_word(word_list=word_list)

            if len(password + new_word) > max_password_length:
                attempt_counter += 1
                continue

            password += new_word
            # Reset and allow 3 more attempts
            attempt_counter = 0

        return password

    @classmethod
    def generate_password(
        cls,
        dictionary_file_path: t.Optional[pl.Path],
        min_word_length: int = 4,
        max_word_length: int = 8,
        min_password_length: int = 10,
        max_password_length: int = 20,
        separator: str = "",
    ) -> str:
        generator = cls(dictionary_file_path=dictionary_file_path)

        # Filter the allowed word set early to reduce memory intensity
        word_list = generator.load_and_filter_library(
            min_word_length=min_word_length, max_word_length=max_word_length
        )
        logger.debug(f"Base word list loaded: {word_list}")

        password = generator.construct_password(
            word_list=word_list,
            min_password_length=min_password_length,
            max_password_length=max_password_length,
            separator=separator,
        )

        return password
