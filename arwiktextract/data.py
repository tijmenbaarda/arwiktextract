from pathlib import Path
import json
import requests
import pickle
import sqlite3
from typing import Optional, Union
import logging

from arwiktextract import datadir
from .normalizer import normalize

logger = logging.getLogger(__file__)


class WiktextractException(RuntimeError):
    pass


class Data:
    DATA_URL = (
        "https://kaikki.org/dictionary/Arabic/kaikki.org-dictionary-Arabic.json"
    )
    data = None
    index = None
    originaldatafile: Path
    databasefile: Path
    con: Optional[sqlite3.Connection] = None

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
        print(f"Successfully saved database to {self.originaldatafile}.")

    def _connect_db(self):
        self.con = sqlite3.connect(self.databasefile)

    def _create_tables(self):
        if self.con is None:
            self._connect_db()
        assert self.con is not None
        cur = self.con.cursor()
        cur.execute(
            """
CREATE TABLE entries(id INTEGER PRIMARY KEY,
                     content TEXT);
CREATE TABLE lookup(id INTEGER PRIMARY KEY,
                    form TEXT,
                    entry INTEGER,
                    FOREIGN KEY(lookup) REFERENCES entries(id));
        """
        )

    def _process_database(self):
        print("Processing database...")
        self.data = []
        self.index = {}
        no_forms = 0
        f = open(self.originaldatafile)
        for line in f:
            data = json.loads(line)  # TODO: error check
            # TODO: Skip inflected forms (or not...)
            if "forms" not in data:
                no_forms += 1
                continue
            self.data.append(data)
            current_index = len(self.data) - 1
            for formdata in data["forms"]:
                form = formdata["form"]
                normalized = normalizer.normalize(form)
                if normalized not in self.index:
                    self.index[normalized] = [current_index]
                else:
                    self.index[normalized].append(current_index)
        f.close()
        print("Processing database successful. Items without form: {}".format(no_forms))

    def _save_processed_database(self):
        print("Saving processed database...")
        with open(self.processeddatafile, "wb") as f:
            combined = (self.data, self.index)
            pickle.dump(combined, f)

    def _load_processed_database(self):
        print("Loading processed database...")
        with open(self.processeddatafile, "rb") as f:
            combined = pickle.load(f)
        self.data, self.index = combined

    def _prepare_data(self):
        if not self.originaldatafile.exists():
            self._download_database()
        if not self.processeddatafile.exists():
            self._process_database()
            self._save_processed_database()
        else:
            self._load_processed_database()
