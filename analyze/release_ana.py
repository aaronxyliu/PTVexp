import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
import sys
import json

tables = conn.show_tables()

for table_name in tables:
    cnt = conn.entry_count(table_name)
    if cnt == 0:
        conn.drop(table_name)