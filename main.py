#!/bin/env python3
from view.gtk import main
from store.sqlite import SqliteStore
from glob import glob

if __name__ == "__main__":
    db = SqliteStore(':memory:')
    main(db)
