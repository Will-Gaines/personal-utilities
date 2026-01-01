import click
import pathlib as pl
import typing as t

from src.password_generator import password_generator as pg


@click.command(name="generate-password")
@click.option(
    "--dictionary-path",
    default=None,
    help="Path to the file to use as your dictionary base",
)
@click.option(
    "--min-word-length", default=4, help="The shortest word length to use (inclusive)"
)
@click.option(
    "--max-word-length", default=4, help="The longest word length to use (inclusive)"
)
@click.option(
    "--min-password-length",
    default=4,
    help="The shortest total password length to reach",
)
@click.option(
    "--max-password-length",
    default=4,
    help="The longest total password length to reach",
)
@click.option(
    "--separator",
    default="",
    help="The character to concatenate words with in the password",
)
def generate_password(
    min_word_length: int,
    max_word_length: int,
    min_password_length: int,
    max_password_length: int,
    separator: str,
    dictionary_path: t.Optional[pl.Path] = None,
):
    password = pg.PasswordGenerator.generate_password(
        dictionary_file_path=None or pl.Path(dictionary_path),
        min_word_length=min_word_length,
        max_word_length=max_word_length,
        min_password_length=min_password_length,
        max_password_length=max_password_length,
        separator=separator,
    )
    click.echo(f"Your generated password is...  {password}")
