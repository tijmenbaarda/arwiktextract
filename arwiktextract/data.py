from pathlib import Path
import json
import requests
import sqlite3
from typing import Optional, Union
import logging

from arwiktextract import datadir
from .normalizer import normalize
from .entry import Entry

logger = logging.getLogger(__file__)


class WiktextractError(RuntimeError):
    pass


class NotFoundError(WiktextractError):
    pass


class Data:
    DATA_URL = "https://kaikki.org/dictionary/Arabic/kaikki.org-dictionary-Arabic.json"
    originaldatafile: Path
    databasefile: Path
    con: Optional[sqlite3.Connection] = None
    cur: Optional[sqlite3.Cursor] = None

    def __init__(self, data_directory: Optional[Union[Path, str]] = None):
        if data_directory is None:
            data_directory = datadir
        elif not isinstance(data_directory, Path):
            data_directory = Path(data_directory)
        self.originaldatafile: Path = data_directory / "wiktionary-arabic.json"
        self.databasefile: Path = data_directory / "db.sqlite3"

    def _download_database(self):
        logger.info("Downloading database...")
        response = requests.get(self.DATA_URL)
        if response.ok:
            try:
                self.originaldatafile.parent.mkdir(exist_ok=True, parents=True)
                with open(self.originaldatafile, "wb") as f:
                    f.write(response.content)
            except OSError as err:
                raise WiktextractError(
                    f"Error writing database file to disk: {err}"
                )
        else:
            raise WiktextractError(
                f"Error downloading database file from {self.DATA_URL}"
            )
        logger.info(f"Successfully saved database to {self.originaldatafile}.")

    def _connect_db(self):
        self.con = sqlite3.connect(self.databasefile)
        self.cur = self.con.cursor()

    def _disconnect_db(self):
        if not self.con:
            return
        self.cur = None
        self.con.close()

    def _create_tables(self):
        if self.con is None:
            self._connect_db()
        assert self.con is not None
        assert self.cur is not None
        self.cur.execute(
            """
CREATE TABLE entry(id INTEGER PRIMARY KEY,
                   content TEXT);
        """
        )
        self.cur.execute(
            """
CREATE TABLE form(id INTEGER PRIMARY KEY,
                  form TEXT,
                  entry INTEGER,
                  CONSTRAINT no_duplicates UNIQUE (form, entry)
                  FOREIGN KEY(entry) REFERENCES entries(id));
        """
        )

    def _add_entry(self, index: int, data: str):
        assert self.cur is not None
        assert self.con is not None
        self.cur.execute("INSERT INTO entry(id, content) VALUES(?, ?);", (index, data))

    def _add_form(self, form: str, index: int):
        assert self.cur is not None
        assert self.con is not None
        self.cur.execute(
            "INSERT OR IGNORE INTO form(form, entry) VALUES(?, ?);", (form, index)
        )

    def _process_database(self):
        logger.info("Processing database...")
        no_forms = 0
        f = open(self.originaldatafile)
        if self.con:
            self.con.close()
        if self.databasefile.exists():
            logger.info("Deleting already existing database file")
            self.databasefile.unlink()
        self._connect_db()
        self._create_tables()
        assert self.con is not None
        for index, line in enumerate(f):
            if index > 0 and index % 1000 == 0:
                print(f"{index} items processed")
                self.con.commit()
            try:
                data = json.loads(line)
                assert isinstance(data, dict)
            except json.JSONDecodeError as err:
                raise WiktextractError(f"Error processing Wiktextract data: {err}")
            # TODO: Skip inflected forms (or not...)
            if "forms" not in data:
                no_forms += 1
                continue
            self._add_entry(index, line)
            for formdata in data["forms"]:
                form = formdata["form"]
                normalized = normalize(form)
                self._add_form(normalized, index)
        self.con.commit()
        f.close()
        print("Processing database successful. Items without form: {}".format(no_forms))

    def prepare_data(self, refresh=False):
        if not self.originaldatafile.exists() or refresh:
            self._download_database()
        if not self.databasefile.exists() or refresh:
            self._process_database()
        self._connect_db()

    def get_by_index(self, index: int) -> Entry:
        self.prepare_data()
        assert self.cur is not None
        res = self.cur.execute("SELECT content FROM entry WHERE id=?", (index,))
        result = res.fetchone()
        if result is None:
            raise NotFoundError()
        data_json = result[0]
        try:
            data = json.loads(data_json)
        except json.JSONDecodeError as err:
            raise WiktextractError(f"Error parsing content in database: {err}")
        return Entry(data=data)

    def get_indices_by_normalized_form(self, form: str) -> list[int]:
        self.prepare_data()
        assert self.cur is not None
        res = self.cur.execute("SELECT entry FROM form WHERE form=?", (form,))
        result = res.fetchall()
        return [int(x[0]) for x in result]

    def get_by_normalized_form(self, form: str) -> list[Entry]:
        indices = self.get_indices_by_normalized_form(form)
        return [self.get_by_index(x) for x in indices]

    def get_by_form(self, form: str) -> list[Entry]:
        """Return entries that match with the given form. The form may 
        or may not contain vowel signs, hamzas and other special characters,
        and only if present they will be taken into account."""
        # First get all entries that may match according to the fully
        # normalized form
        entries = self.get_by_normalized_form(normalize(form))
        return [entry for entry in entries if entry.find_matching_forms(form)]
