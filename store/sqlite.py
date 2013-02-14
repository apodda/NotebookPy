import sqlite3

from utils import parse_title
from store.store import *

# FIXME make sure changes are committed to disk (implement commit)
class SqliteStore(Store): 
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
        # FIXME quote sqlite docs?
        # FIXME virtual tables SELECT statement 'ignore' 'id' (but not 'rowid') 
        # Since we declared id an integer primary key, it becomes an alias for ROWID,
        # and searches by id will be faster. Also, sqlite will NOT change the rowid
        # in VACUUM calls
        # If we declare it AUTOINCREMENT, it will also ensure that the same rowid
        # will not be reused (ie, the selection algorithm for IDs is guaranteed
        # to be monotonically increasing)
        self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes "
                        "USING fts4("
                        "title, "
                        "body, "
                        "id INTEGER PRIMARY KEY"
                        ")")
        
    def update_note(self, text, rowid):
        """Update note based on rowid. Parses title from text.
        
        Parameters
        ----------
        text: str
              The text of the note, to be updated in db
        rowid: int
             Unique id of the note. Must be non-empty. 
        """
        if rowid == '':
            raise WriteError
        # BUG? Sqlite does return nothing if we search by 'id' (or any INTEGER
        # PRIMARY KEY) rather than 'rowid'. This happens only with a virtual
        # table
        self.db.execute("UPDATE notes SET body=? WHERE rowid=?", [text, rowid]) 
        self.db.execute("UPDATE notes SET title=? WHERE rowid=?", [parse_title(text), rowid])
    
    def query(self, query):
        """Takes a query in extended query syntax, returns a list of titles and IDs
        (integers)
                
        Parameters
        ----------
        query: str
        """
        if query != '':
            return [[title, rowid] for title, rowid # cursor.execute expects a list!
                in self.db.execute("SELECT title, rowid FROM notes WHERE body MATCH ?", [query])]
        else:
            return [[title, rowid] for title, rowid 
                in self.db.execute("SELECT title, rowid FROM notes")]

    def commit(self):
        self.db.commit()

    def get_text(self, rowid):
        """Returns the text of a note given the rowids
        
        Parameters
        ----------
        rowid: int
        """
        if rowid is None: # Is this needed in any way?
            raise ReadError("Empty ID")
        cur = self.db.execute("SELECT body FROM notes WHERE rowid=?", [rowid])
        t = cur.fetchone()
        if t is None:
            raise ReadError("No note matches ID " + str(rowid))
        else:
            text = t["body"]
            return text
        
    def add_note(self, text):
        """Adds a note to db. Returns the note title and its rowid (an int).
        
        Parameters
        ----------
        text = str
                Text of the note to be created. 
        """
        title = parse_title(text)
        # From Sqlite documentation:
        # >If you declare a column of a table to be INTEGER PRIMARY KEY, 
        #  then whenever you insert a NULL into that column of the table, the
        #  NULL is automatically converted into an integer which is one greater 
        #  than the largest value of that column over all other rows in the table,
        #  or 1 if the table is empty. (If the largest possible integer key, 
        #  9223372036854775807, then an unused key value is chosen at random.)
        self.db.execute("INSERT INTO notes VALUES (?, ?, NULL)", [title, text])
        # last_insert_rowid() is actually a C/C++ api call, so it needs the
        # parentesis
        cur = self.db.execute("SELECT last_insert_rowid();")
        rowid = cur.fetchone()[0]
        return title, rowid
        
    def delete_note(self, rowid):
        """Deletes note from db, given its rowid.
        
        Parameters
        ----------
        rowid = int
                rowid of the row to be deleted
        """
        self.db.execute("DELETE FROM notes WHERE rowid=?", [rowid])
