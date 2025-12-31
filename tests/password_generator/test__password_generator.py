import pathlib as pl

import pytest

from src.password_generator import password_generator as pg


def test__initialise_password_generator_class():
    generator = pg.PasswordGenerator()

    assert isinstance(generator, pg.PasswordGenerator)


def test__init_with_bad_file_raises_error():
    missing_file = pl.Path(__file__) / "i_dont_exist.txt"

    with pytest.raises(FileNotFoundError):
        pg.PasswordGenerator(dictionary_file_path=missing_file)


def test__init_with_override_file(tmp_path):
    new_dictionary = tmp_path / "some_new_dictionary_file.txt"
    new_dictionary.touch()

    generator = pg.PasswordGenerator(new_dictionary)

    assert isinstance(generator, pg.PasswordGenerator)
    assert generator.dictionary_file_path == new_dictionary


def test__load_and_filter_library(tmp_path, mock_word_list):
    # Set up our temp file with mock data. In other tests we can mock the pathlib read method
    # but here we explicitly want to test loading it from file
    new_dictionary = tmp_path / "some_new_dictionary_file.txt"
    new_dictionary.touch()
    new_dictionary.write_text(data="\n".join(mock_word_list))

    generator = pg.PasswordGenerator(dictionary_file_path=new_dictionary)
    word_list = generator.load_and_filter_library(
        min_word_length=2,
        max_word_length=4,
    )

    assert word_list == ["bee", "do"]

    # Test that we can validly return an empty list in some cases
    shorter_word_list = generator.load_and_filter_library(
        min_word_length=1,
        max_word_length=1,
    )
    assert not shorter_word_list


def test__load_and_filter_raises_value_error():
    generator = pg.PasswordGenerator()

    with pytest.raises(ValueError):
        generator.load_and_filter_library(min_word_length=10, max_word_length=2)


def test__pick_random_word(monkeypatch):
    monkeypatch.setattr(
        "src.password_generator.password_generator.r.randint", lambda a, b: 0
    )

    generator = pg.PasswordGenerator()
    random_word = generator.pick_random_word(word_list=["some", "random", "words"])

    assert random_word == "Some"


def test__construct_password(monkeypatch):
    monkeypatch.setattr(
        "src.password_generator.password_generator.r.randint", lambda a, b: 0
    )

    generator = pg.PasswordGenerator()
    generated_password = generator.construct_password(
        word_list=[
            "this",
            "is",
            "our",
            "password",
            "these",
            "words",
            "areToo",
            "verbose",
        ],
        min_password_length=15,
        max_password_length=20,
        separator="|",
    )

    assert generated_password == "This|Is|Our|Password"


def test__construct_password__additional_word(monkeypatch):
    monkeypatch.setattr(
        "src.password_generator.password_generator.r.randint", lambda a, b: 0
    )

    generator = pg.PasswordGenerator()
    # Test that, even though ThisIsOurPassword is of minimum required length, adding oneMore would not go
    # over the limit, so we add one more word
    generated_password = generator.construct_password(
        word_list=[
            "this",
            "is",
            "our",
            "password",
            "oneMore",
            "these",
            "words",
            "areToo",
            "verbose",
        ],
        min_password_length=16,
        max_password_length=24,
    )

    assert generated_password == "ThisIsOurPasswordOnemore"


def test__generate_password__class_method(monkeypatch, tmp_path, mock_word_list):
    monkeypatch.setattr(
        "src.password_generator.password_generator.r.randint", lambda a, b: 0
    )

    # Set up our mock dictionary
    mock_word_file = tmp_path / "mock_dictionary.txt"
    mock_word_file.touch(exist_ok=True)
    mock_word_file.write_text(data="\n".join(mock_word_list))

    password = pg.PasswordGenerator.generate_password(
        dictionary_file_path=mock_word_file,
        min_password_length=16,
        max_password_length=24,
        min_word_length=4,
        max_word_length=10,
        separator="-",
    )

    assert password == "Apple-Calculator-Engine"
