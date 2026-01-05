import json
import logging

from click.testing import CliRunner

from src.cli import cli


logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)


def cli_mocker(*args, **kwargs) -> None:
    """
    A function for re-use in CLI testing, as it will log out the args and kwargs passed from the CLI to
    the main function
    Prints args as a comma separated list, and kwargs as a json object
    eg args: 'hello', 'world'... keyword args: '{"foo": "bar"}'
    :param args:
    :param kwargs:
    :return:
    """
    logger.info(
        f"Provided arguments are... args: {', '.join(args)}... keyword args: {json.dumps(kwargs)}"
    )


def test__cli__test():
    runner = CliRunner()
    result = runner.invoke(cli, ["test"])

    assert result.output.strip() == "Cli installation successful!"


def test__cli__password_generator(monkeypatch):
    class MockGenerator:
        @classmethod
        def generate_password(cls, *args, **kwargs):
            return cli_mocker(args, kwargs)

    monkeypatch.setattr("src.cli.pg", "PasswordGenerator", MockGenerator)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate_password",
            "--dictionary-path",
            "some/path/to/dictionary.txt",
            "--min-word-length",
            2,
            "--max-word-length",
            10,
            "--min-password-length",
            20,
            "--max-password-length",
            30,
            "--separator",
            "|",
        ],
    )

    args_dictionary = {
        "dictionary-path": "some/path/to/dictionary.txt",
        "min-word-length": 2,
        "max-word-length": 10,
        "min-password-length": 20,
        "max-password-length": 30,
        "separator": "|",
    }

    assert json.dumps(args_dictionary).strip() in result.output.strip()
