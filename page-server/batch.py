import pprint
from app import app, db
from sqlalchemy import inspect

pp = pprint.PrettyPrinter()

ins = inspect(db.engine)
tables = ins.get_table_names()
for table in tables:
    for column in ins.get_columns(table):
        pp.pprint(column)