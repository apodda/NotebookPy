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

#def test_update_files(non_empty_db):
#    db, tmp = non_empty_db
#    db.update_note('Minivan\nMinivan', 1) # Sqlite rowids begin from 1 unless you say otherwise
#    db.commit()
#    sleep(1)
#    assert exists(pjoin(tmp.name, 'Minivan.txt'))

# Check if file on disk are updated/deleted on commit 
def test_files(db):
    db, tmp = db
    uid = db.add_note('Minivan')
    db.commit()
    sleep(1)
    assert exists(pjoin(tmp.name, 'Minivan.txt'))
    with open(pjoin(tmp.name, 'Minivan.txt'), 'r') as f:
        assert f.read() == 'Minivan'
    
    db.update_note('Minibus', uid)
    db.commit()
    sleep(1)
    assert exists(pjoin(tmp.name, 'Minibus.txt'))
    with open(pjoin(tmp.name, 'Minibus.txt'), 'r') as f: 
        assert f.read() == 'Minibus'
    
    db.delete_note(uid)
    db.commit()
    sleep(1)
    assert not exists(pjoin(tmp.name, 'Minibus.txt'))

# Check if the list of edited notes is update on note change
def test_wal(db):
    db, tmp = db
    uid = db.add_note('Minivan')
    assert [x for x in db.db.execute('select * from wal')] != []
    db.commit()
    assert [x for x in db.db.execute('select * from wal')] == []
    db.update_note('Minibus', uid)
    assert [x for x in db.db.execute('select * from wal')] != []

def test_wrong_id_exception(db):
    db, tmp = db
    with pytest.raises(ReadError):
        db.get_text(randint(5,100000))
        db.get_text(randint(5,100000))
        db.get_text(randint(5,100000))
