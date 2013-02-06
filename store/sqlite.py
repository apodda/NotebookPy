import sqlite3
from utils import parse_title
from uuid import uuid4

class WriteError(RuntimeError):
    pass

class ReadError(RuntimeError):
    pass

class StoreError(RuntimeError):
    pass

class SqliteStore(): # FIXME make sure changes are committed
    def __init__(self, path):
        """Costructor, takes path to an existing database. If it doesn't exist,
           sqlite will create it for us. Will create a table called 'notes' if
           it doesn't exist. The table will use fts4 fulltext search to speed
           up searches
        
           Parameters
           ----------
           path: str
                 Path to database. Might take ':memory:' to create a database in memory.
        """
        self.db = sqlite3.connect(path)
        #self.db.isolation_level = None # Turns on autocommit!
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes USING fts4(title, body, id)")

        
    def update_note(self, text, uid):
        """Update note based on uid. Parses title from text.
        
        Parameters
        ----------
        text: str
              The text of the note, to be updated in db
        uid: str
             Unique id of the note. Must be non-empty. 
        """
        if uid == '':
            raise WriteError # FIXME is there a way to check that uid is a good UUID?
        self.db.execute("UPDATE notes SET body=? WHERE id=?", [text, uid]) 
        self.db.execute("UPDATE notes SET title=? WHERE id=?", [parse_title(text), uid])
    
    def query(self, query):
        """Takes a query in extended query syntax, returns a list of titles and UUIDs
        
        Parameters
        ----------
        query: str
        """
        if query != '':
            return [[title, uid] for title, uid # cursor.execute expects a list!
                in self.db.execute("SELECT title, id FROM notes WHERE body MATCH ?", [query])]
        else:
            return [[title, uid] for title, uid 
                in self.db.execute("SELECT title, id FROM notes")]

    def get_text(self, uid):
        """Returns the text of a note given the UUIDs
        
        Parameters
        ----------
        uid: str
        """
        if uid == '':
            raise ReadError("Empty UUID") # FIXME is there a way to check that uid is a good uid?
        cur = self.db.execute("SELECT body FROM notes WHERE id=?", [uid])
        t = cur.fetchone()
        if t is None:
            raise ReadError("No note matches UUID " + uid)
        else:
            text = t["body"]
            return text
        
    def add_note(self, text):
        """Adds a note to db, and creates an UUID for it. Returns the note title and UUIDs.
        
        Parameters
        ----------
        text = str
                Text of the note to be created. 
        """
        #if text == '':
        #    raise WriteError
        uid = str(uuid4())
        title = parse_title(text)
        self.db.execute("INSERT INTO notes VALUES (?, ?, ?)", [title, text, uid])
        return title, uid
        
    def delete_note(self, uid):
        """Deletes note from db, given its UUID.
        
        Parameters
        ----------
        uid = str
                UUID of the row to be deleted
        """
        self.db.execute("DELETE FROM notes WHERE id=?", [uid])
