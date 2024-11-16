import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')

NO = 60

OUTPUT_TABLE = f'result11'


if __name__ == '__main__':
    tables = conn.show_tables()

    combine_tables = ['result11_5','result11_6']

    conn.combine_tables(OUTPUT_TABLE, combine_tables)
    logger.custom("output table size", conn.entry_count(OUTPUT_TABLE))
    conn.close()








