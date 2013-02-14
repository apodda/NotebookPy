import sqlite3
from os.path import join as pjoin
from os.path import isdir, exists
from glob import glob

from utils import parse_title
from store.store import *
from store.sqlite import SqliteStore

class FSStore(SqliteStore):
    def __init__(self, path):
        """Takes path of note directory, and creates a db in it if it doesn't
           exist.
        """
        if not isdir(path):
            raise StoreError(path + ' is not a valid directory')
        
        self.path = path
        dbpath = pjoin(path, '.notes.db')
        if exists(dbpath):
            self.db = sqlite3.connect(dbpath)

            # FIXME check if notes have been altered.
        else: #Import all .txt files into the database
            self.db = sqlite3.connect(dbpath)
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes "
                            "USING fts4("
                            "title, "
                            "body, " # Text of the note
                            "id INTEGER PRIMARY KEY"
                            ")")
            for fn in glob(pjoin(path, '*.txt')):
                with open(fn, 'r') as f:
                    # FIXME Here we assume notes aren't really BIG
                    text = f.read()
                    self.db.execute("INSERT INTO notes VALUES (?, ?, NULL)", 
                                    [parse_title(text), text])
