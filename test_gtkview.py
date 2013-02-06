import pytest
from utils import parse_title
from store.sqlite import SqliteStore, ReadError
from view.gtk import Handler
from gi.repository import Gtk
from uuid import uuid4

@pytest.fixture
def build_window():
    """Surrogate for main(), builds window from glade files
    without showing them/ starting Gtk.main()
    """
    db = SqliteStore(':memory:')
    
    builder = Gtk.Builder()
    builder.add_from_file("view/notebook.glade")
    notes = ['0 Test Note', '1 Test Note', '2 Test Note', '3 Test Note']
    
    # Glade does not accept python types for Liststore, so we have to build 
    # the model in python
    liststore = Gtk.ListStore(str, str) # Title and uuid
    for n in notes:
        db.add_note(n)
    
    view = builder.get_object("treeview_notelist")
    view.set_model(liststore)
    
    selection = builder.get_object("treeview_notelist_selection")
    selection.select_iter(liststore.get_iter("0")) # 0 means first note, no search in-tree
    
    textbuffer = builder.get_object("current_note_buffer")
    
    handler = Handler(liststore, liststore.get_iter("0"), db)
    builder.connect_signals(handler)
    
    return builder, handler, liststore, selection, textbuffer, db
