import pytest
from os.path import join as pjoin
from os.path import isdir, exists
from tempfile import TemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir
from random import randint
from time import sleep

from utils import parse_title
from store.fs import FSStore
from store.store import ReadError

@pytest.fixture
def db():
    tmp = TmpDir()
    db = FSStore(tmp.name)
    return db, tmp

@pytest.fixture
def non_empty_db():
    notes = ['Lorem Ipsum\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
         'Section 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC\nSed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.',
         '1914 translation by H. Rackham\nBut I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.']

    tmp = TmpDir()
    for note in notes:
        with open(pjoin(tmp.name, (parse_title(note) + '.txt')), 'w') as f:
            f.write(note)
    
    assert not exists(pjoin(tmp.name, '.notes.db'))
    db = FSStore(tmp.name)
    return db, tmp

def test_db_is_created(db):
    db, tmp = db
    assert exists(pjoin(tmp.name, '.notes.db'))
    
def test_notes_in_db(non_empty_db):
    db, tmp = non_empty_db
    assert db.query('') is not None
    assert db.query('') != []
    assert db.query('Lorem') is not None
    assert db.query('Lorem') != []

# Check if file on disk are updated/deleted on add/rename/delete/etc
def test_files(db):
    db, tmp = db
    uid = db.add('Minivan')
    db.select(uid)
    sleep(1)
    
    assert exists(pjoin(tmp.name, 'Minivan.txt'))
    with open(pjoin(tmp.name, 'Minivan.txt'), 'r') as f:
        assert f.read() == ''
    
    db.update('Minibus')
    sleep(1)
    with open(pjoin(tmp.name, 'Minivan.txt'), 'r') as f: 
        assert f.read() == 'Minibus'
    
    
    db.rename('Macrobus')
    sleep(1)
    assert not exists(pjoin(tmp.name, 'Minivan.txt'))
    assert exists(pjoin(tmp.name, 'Macrobus.txt'))
        
    db.delete()
    #db.commit()
    sleep(1)
    assert not exists(pjoin(tmp.name, 'Macrobus.txt'))

# Check if the db is updated on add/rename/delete/etc
def test_files(db):
    db, tmp = db
    uid = db.add('Minivan')
    db.select(uid) 
    assert 'Minivan' in [row["title"] for row in db.db.execute("select title from notes")]
    assert 'Minivan' in db.query('')[0]
    
    db.update('Minibus')
    assert 'Minibus' in [row["text"] for row in db.db.execute("select text from notes")]
    assert 'Minivan' in db.query('')[0]
    assert 'Minibus' in db.get()

    db.rename('Macrobus')
    assert 'Macrobus' in [row["title"] for row in db.db.execute("select title from notes")]
    assert 'Macrobus' in db.query('')[0]

    db.delete()
    assert [] == [row["title"] for row in db.db.execute("select title from notes")]
    assert [] == db.query('')

def test_wrong_id_exception(db):
    db, tmp = db
    uid = db.add('Minivan')
    db.select(uid)
    with pytest.raises(ReadError):
        db.select(randint(5,100000))
        db.select(randint(5,100000))
        db.select(randint(5,100000))
    assert db.current_note["id"] == uid
