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
           exist. Loads .txt files from directory into the database
           
        Parameters
        ----------
        path: Directory where notes and db should be
        """
        if not isdir(path):
            raise StoreError(path + ' is not a valid directory')
        
        self.path = path
        dbpath = pjoin(path, '.notes.db')
        if exists(dbpath):
            self.db = sqlite3.connect(dbpath)
            # TODO check if notes have been altered.
        else: #Import all .txt files into the database
            self.db = sqlite3.connect(dbpath)
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes "
                            "USING fts4("
                            "title, "
                            "body, " # Text of the note
                            "id INTEGER PRIMARY KEY"
                            ")")
            # FIXME rename wal to something more accurate/expressive
            self.db.execute("CREATE TABLE IF NOT EXISTS wal("
                            # ID of the note which have been modified 
                            "noteid,"
                            # Name of the note on disk. 'Null' if it's a new note
                            "filename"
                            ")")
            # TODO Handle more cases
            for fn in glob(pjoin(path, '*.txt')):
                with open(fn, 'r') as f:
                    # FIXME Here we assume notes aren't really BIG
                    text = f.read()
                    self.db.execute("INSERT INTO notes VALUES (?, ?, NULL)", 
                                    [parse_title(text), text])
                                    
    def update_note(self, text, rowid):
        pass
    
    def delete_note(self, rowid):
        pass
        
    def commit(self):
        pass
