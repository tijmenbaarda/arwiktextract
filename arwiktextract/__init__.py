from appdirs import AppDirs
from pathlib import Path

datadir = Path(AppDirs("arwiktextract", "cdh").user_data_dir)
