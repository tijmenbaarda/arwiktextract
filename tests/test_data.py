from pathlib import Path
import pytest

from arwiktextract.data import Data


@pytest.fixture
def datawithtestdata(tmp_path: Path):
    data = Data(tmp_path)
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

    def test_download_database(self, datawithtestdata):
        pass
