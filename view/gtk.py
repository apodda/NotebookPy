from gi.repository import Gtk
from utils import parse_title
import pdb

class Handler:
    # Since liststore isn't created with the gtkBuilder, it can't be passed
    # as user data by signals.
    def __init__(self, liststore, selection, textbuffer, view, db):
        self.liststore = liststore
        self.textbuffer = textbuffer
        self.selection = selection
        self.view = view
        _, self.cursor = self.selection.get_selected()
        self.db = db
        
        self.lock = False
    
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_current_note_buffer_changed(self, tb):
        """ Called when text in the main buffer is changed. This
            means it's called when switching notes too.
        """
        if not self.lock:
            text = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                            self.textbuffer.get_end_iter(),
                                            False)
            uid = self.liststore[self.cursor][1]
            self.db.update_note(text, uid)
            self.liststore[self.cursor][0] = parse_title(text)

    def on_treeview_notelist_selection_changed(self, selection):
        """Called when selection is changed. Ensure that the text in the
           buffer is committed to the db, unless it's empty. If the note
           was not yet in the db, we also add the uid to the store.
           Also updates the cursor and the textbuffer to the current selection
        """
        # If lock is true, other callback functions are modifying the liststore
        # therefore we should do nothing!
        if not self.lock:
            text = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                            self.textbuffer.get_end_iter(),
                                            False)

            olduid = self.liststore[self.cursor][1]
            oldcursor = self.cursor

            _, self.cursor = self.selection.get_selected()
            newuid = self.liststore[self.cursor][1]

#            if olduid != newuid and text == '':
#                if text == '': # delete or update old note
#                    self.db.delete_note(olduid)
#                    self.liststore.remove(oldcursor)
#                else:
#                    self.db.update_note(text, olduid)
#                self.textbuffer.set_text(self.db.get_text(newuid))
            if olduid != newuid:
                self.lock = True
                if text == '': # delete or update old note
                    self.db.delete_note(olduid)
                    self.liststore.remove(oldcursor)
                self.textbuffer.set_text(self.db.get_text(newuid))
                
                self.lock = False

    def search_buffer_inserted_text_cb(self, widget, pos, addtext, number):
        """ Callback for text insert in search entry:

        Parameters
        ----------
        widget: GtkEntry or GtkSearchEntry
        pos: int
             position of the inserted characters
        addtext: str
                 added characters
        num: int
             number of added characters
        """
        # FIXME: should the search entry be passed to the handler?
        self.reset_tree(widget.get_text())

    def search_buffer_deleted_text_cb(self, widget, pos, num):
        """ Callback for text insert in search entry:

        Parameters
        ----------
        widget: GtkEntry or GtkSearchEntry
        pos: int
             position of the deleted characters
        num: int
             number of deleted characters
        """
        self.reset_tree(widget.get_text())


    def new_note_activate_cb(self, widget):
        self.new_note_from_text(widget, '')
        
    def new_note_from_clipboard_activate_cb(self, widget):
        pass

    def delete_note_activate_cb(self, widget):
        self.lock = True
        
        oldcursor = self.cursor
        olduid = self.liststore[oldcursor][1]
        
        # Check which note to select next. We there aren't any other notes,
        # create one and select that
        if self.liststore.iter_next(oldcursor) is not None:
            self.cursor = self.liststore.iter_next(oldcursor)
        elif self.liststore.iter_previous(oldcursor) is not None:
            self.cursor = self.liststore.iter_previous(oldcursor)
        else:
            self.cursor = self.liststore.append(self.db.add_note(''))
        
        # Select new note
        newuid = self.liststore[self.cursor][1]
        self.selection.select_iter(self.cursor)
        self.textbuffer.set_text(self.db.get_text(newuid))
        
        # Remove old note
        self.db.delete_note(olduid)
        self.liststore.remove(oldcursor)
        
        self.lock = False
        
    def new_note_from_text(self, widget, newtext):
        self.lock = True
        oldtext = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                        self.textbuffer.get_end_iter(),
                                        False)
        if oldtext != '':
            title, uid = self.db.add_note(newtext)
            treeiter = self.liststore.append([title, uid])
        
            self.selection.select_iter(treeiter)
            self.textbuffer.set_text(newtext)
            self.cursor = treeiter
        
        self.lock = False

    def reset_tree(self, querystr):
        """Helper function, queries the db on text change.
        
        Parameters
        ----------
        querystr: str
        """
        self.lock = True
        
        # We should commit text to the db first, or delete the current note
        # if it's empty. (if we don't do this, we'll clutter the db with
        # empty notes)
        # TODO: do all text commits when the buffer loses focus.
        # TODO: write an helper function to do the commit
        # FIXME? Maybe we should implement a 'temporary note' in the db, which
        # would be promoted to a proper one and inserted in the db when non-empty
        # TODO test all methods of the handler to ensure that they always set
        # a valid cursor
        text = self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                        self.textbuffer.get_end_iter(),
                                        False)
        uid = self.liststore[self.cursor][1]
        if text != '':
            self.db.update_note(text, uid)
        else:
            self.db.delete_note(uid)
        
        self.liststore.clear()
        self.textbuffer.delete(self.textbuffer.get_start_iter(),
                               self.textbuffer.get_end_iter())
        
        # If the query returns nothing, create an empty note and select it
        results = self.db.query(querystr)
        if results != []:
            for title, uid in results:
                self.liststore.append([title, uid])
        else:
            self.liststore.append(self.db.add_note(''))
        
        # Update cursor, selection and textbuffer
        self.cursor = self.liststore.get_iter("0")
        self.selection.select_iter(self.cursor)
        self.textbuffer.set_text(self.db.get_text(self.liststore[self.cursor][1]))
        
        self.lock = False


def main(db, debug=False):
    builder = Gtk.Builder()
    builder.add_from_file("view/notebook.glade")

    liststore = builder.get_object("liststore")
    view = builder.get_object("treeview_notelist")
    textbuffer = builder.get_object("current_note_buffer")
    selection = builder.get_object("treeview_notelist_selection")

    # Populate the liststore. Set the text buffer to the first note text if
    # the note db is non-empty
    query = db.query('')
    if query != []:
        for title, uid in query:
            liststore.append([title, uid])

            textbuffer.set_text(db.get_text(query[0][1])) # 0,1 means first note, uid
    else:
        liststore.append(db.add_note('')) # Handle empty db

    # Make sure the first note is selected
    selection.select_iter(liststore.get_iter("0")) # 0 means first note, no search in-tree

    handler = Handler(liststore, selection, textbuffer, view, db)
    builder.connect_signals(handler)

    if debug is False:
        window = builder.get_object("main_window")
        window.show_all()
        Gtk.main()
    else:
        return handler
