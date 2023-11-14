from pathlib import Path
import pytest

from arwiktextract.data import Data

TESTDATAPATH = Path(__file__).parent / "data" / "wiktionary-arabic.json"


@pytest.fixture
def datawithtestdata(tmp_path: Path):
    """Data object with temporary directory as datapath and a bit of
    test data in originaldatafile"""
    data = Data(tmp_path)
    data.originaldatafile = TESTDATAPATH
    return data


@pytest.fixture(scope="session")
def data_processed(tmp_path_factory):
    data = Data(tmp_path_factory.mktemp("data"))
    data.originaldatafile = TESTDATAPATH
    data.prepare_data()
    return data


class TestData:
    def test_constructor_default(self):
        data = Data()
        assert data.originaldatafile
        assert data.databasefile

    def test_constructor_path(self, tmp_path: Path):
        data = Data(tmp_path)
        assert data.originaldatafile
        assert data.databasefile

    def test_constructor_str(self, tmp_path: Path):
        pathstr = str(tmp_path)
        data = Data(pathstr)
        assert data.originaldatafile
        assert data.databasefile

    def test_connect_db(self, datawithtestdata):
        data = datawithtestdata
        data._connect_db()
        assert data.databasefile.exists()

    def test_close_db(self, datawithtestdata):
        data = datawithtestdata
        data._connect_db()
        data._disconnect_db()

    def test_create_tables(self, datawithtestdata):
        data = datawithtestdata
        data._create_tables()

    def test_process_database(self, datawithtestdata):
        data = datawithtestdata
        data._process_database()

    def test_get_by_index(self, data_processed: Data):
        data = data_processed.get_by_index(0)
        assert isinstance(data, dict)
        assert data["pos"] == "noun"

    def test_get_by_index_not_found(self, data_processed: Data):
        assert data_processed.get_by_index(5000) is None


    def test_get_indices_by_normalized_form(self, data_processed):
        indices = data_processed.get_indices_by_normalized_form("الكتاب")
        assert len(indices) == 2
        assert indices[0] == 0
