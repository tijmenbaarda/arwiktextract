from pathlib import Path
import json
import requests
import sqlite3
from typing import Optional, Union
import logging

from arwiktextract import datadir
from .normalizer import normalize

logger = logging.getLogger(__file__)


class WiktextractException(RuntimeError):
    pass


class Data:
    DATA_URL = "https://kaikki.org/dictionary/Arabic/kaikki.org-dictionary-Arabic.json"
    data = None
    index = None
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
                raise WiktextractException(
                    f"Error writing database file to disk: {err}"
                )
        else:
            raise WiktextractException(
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
        self.data = []
        self.index = {}
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
            try:
                data = json.loads(line)
                assert isinstance(data, dict)
            except json.JSONDecodeError as err:
                raise WiktextractException(f"Error processing Wiktextract data: {err}")
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

    def get_by_index(self, index: int) -> Optional[dict]:
        self.prepare_data()
        assert self.cur is not None
        res = self.cur.execute("SELECT content FROM entry WHERE id=?", (index,))
        result = res.fetchone()
        if result is None:
            return None
        data_json = result[0]
        try:
            data = json.loads(data_json)
        except json.JSONDecodeError as err:
            raise WiktextractException(err)
        return data

    def get_indices_by_normalized_form(self, form: str) -> list[int]:
        self.prepare_data()
        assert self.cur is not None
        res = self.cur.execute("SELECT entry FROM form WHERE form=?", (form,))
        result = res.fetchall()
        return [int(x[0]) for x in result]
