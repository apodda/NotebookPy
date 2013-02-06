#!/bin/env python3
from view.gtk import main
from store.sqlite import SqliteStore

if __name__ == "__main__":
    db = SqliteStore(':memory:')
    main(db)
