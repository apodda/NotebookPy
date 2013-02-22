import sqlite3
from os import unlink
from os import rename as frename
from os.path import join as pjoin
from os.path import isdir, exists, basename
from glob import glob

from utils import parse_title
from store.store import *

class FSStore(Store):
    def __init__(self, path):
        """
        Parameters
        ----------
        path: str
              Path to directory where notes and the database are
        """
        self.path = path
        self.current_note = { "id" : None, # Id of the selected note
                              "file" : None # File object of the selected note
                                          # The file should remain open.
                              }
        dbpath = pjoin(path, '.notes.db')

        if not exists(dbpath):
            self.db = sqlite3.connect(dbpath)
            self.db.row_factory = sqlite3.Row
            self.db.execute("CREATE TABLE IF NOT EXISTS notes"
                    "("
                    "id INTEGER PRIMARY KEY"
                    "title UNIQUE, " # This is used for filenames, so it should be unique
                    "text, "
                    "createdDate, "
                    "modifiedDate"
                    ")")
            for fn in glob(pjoin(path, '*.txt')):
                with open(fn, 'r') as f:
                    # FIXME Here we assume notes aren't really BIG
                    text = f.read()
                    # FIXME Use executemany
                    # TODO handle creation date
                    self.db.execute("INSERT INTO notes VALUES (?, ?, NULL, NULL)",
                                    [basename, text])
        else:
            # TODO Handle existing db
            pass


    def _get_title_from_id(self, uid):
        # FIXME If id doesn't exist?
        cur = self.db.execute("SELECT title FROM notes WHERE id=?",
                                  [uid])
        title = cur.fetchone()[0]

    def _get_current_note_filename(self):
        # TODO as below
        if self.current_note["id"] is None:
            raise StoreError("No note selected")
        else:
            title = self._get_title_from_id(self.current_note['id'])
            return pjoin(self.path, title + '.txt')

    def _ensure_current_note_is_writable(self):
        # TODO Rewrite this in EAFP-style http://docs.python.org/2/glossary.html#term-eafp
        # which basically means, as a try..except
        if self.current_note["file"] is None:
            self.current_note["file"] = open(_get_current_note_filename(), 'w')

    def add(self, title):
        fn = pjoin(path, title + '.txt')
        if exists(fn):
            raise WriteError('FATAL ERROR: File ' + title + '.txt already exists!')
        else:
            # TODO Handle creation and modification date

            # Create an empty file with the right title
            open(fn, 'w').close()

            self.db.execute("INSERT INTO notes VALUES (?, ?, NULL, NULL)", [title, ''])
            cur = self.db.execute("SELECT last_insert_rowid();")
            rowid = cur.fetchone()[0]
            return title, rowid

    def delete(self):
        self.db.execute("DELETE FROM notes WHERE id=?",
                        [self.current_note["id"]])
        unlink(self._get_current_note_filename())

    def get(self):
        cur = self.db.execute("SELECT title, text FROM notes WHERE id=?",
                              [self.current_note["id"]])
        t = cur.fetchone()
        if t is None:
            raise ReadError("No note matches ID " + str(rowid))
        else:
            return t["title"], t["text"] # Relies on row_factory

    def query(self, text):
        # TODO, handle tags, modification and creation date, limit number of
        # returned notes (via SQL limit)
        if query != '':
            return [[title, rowid] for title, rowid # cursor.execute expects a list!
                in self.db.execute("SELECT title, rowid FROM notes"
                                   " WHERE body MATCH ?", [query])]
        else:
            return [[title, rowid] for title, rowid
                in self.db.execute("SELECT title, rowid FROM notes")]

    def rename(self, newtitle):
        frename(self._get_current_note_filename,
                pjoin(self.path, newtitle + '.txt'))

    def select(self, uid):
        self.unselect()
        # TODO check if uid exists!
        self.current_note['id'] = uid
        self._ensure_current_note_is_writable()

    def tag(self, tag):
        pass

    def update(self, text):
        # Updates current note. To update another note, select it first, or
        # use mass_update
        if self.current_note["id"] == None:
            raise StoreError('No note has been selected')
        else:
            self.db.execute("UPDATE notes SET text=? WHERE id=?",
                            [text, self.current_note])
            self._ensure_current_note_is_writable()
            self.current_note['file'].write(text)
            self.current_note['file'].seek(0)

    def unselect(self):
        self.current_note["id"] = None
        self.current_note["file"].close()
        self.current_note["file"] = None

