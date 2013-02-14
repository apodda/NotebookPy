import pytest
from store.store import ReadError
from store.sqlite import SqliteStore
from utils import parse_title
from random import randint

@pytest.fixture
def notes():
    notes = ['Lorem Ipsum\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
         'Section 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC\nSed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.',
         '1914 translation by H. Rackham\nBut I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.']
    return notes

# Set up a db in memory
@pytest.fixture
def db():
    db = SqliteStore(":memory:")
    return db

def test_add_notes(db, notes):
    for note in notes:
        title, _ = db.add_note(note)
        assert title == parse_title(note)

def test_empty_query(db, notes):
    data = [db.add_note(note) for note in notes]
    for title, uid in db.query(''):
        assert (title, uid) in data

def test_nonempty_text_query(db, notes):
    data = [db.add_note(note) for note in notes]
    assert data != None
    for _, uid in data:
        assert db.get_text(uid) != ''

def test_wrong_id_exception(db, notes):
    for note in notes:
        db.add_note(note)
    with pytest.raises(ReadError):
        db.get_text(randint(5,1000000))

def test_lorem_query(db, notes):
    for note in notes:
        db.add_note(note)
    assert 'Lorem Ipsum' in [title for title, _ in db.query('lorem')]
