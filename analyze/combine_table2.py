import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')

NO = 20

OUTPUT_TABLE = f'result_{NO}0k'


if __name__ == '__main__':
    tables = conn.show_tables()

    combine_tables = []
    combine_table_sizes = []
    for index in range(NO - 10, NO):
        table_name = f'result{index}'
        if table_name in tables:
            combine_tables.append(table_name)
            combine_table_sizes.append(conn.entry_count(table_name))
    logger.custom("combined tables", combine_tables)
    logger.custom("combined table sizes", combine_table_sizes)

    conn.combine_tables(OUTPUT_TABLE, combine_tables)
    logger.custom("output table size", conn.entry_count(OUTPUT_TABLE))
    conn.close()








