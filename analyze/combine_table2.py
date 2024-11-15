
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
import pandas as pd

NO = 60

OUTPUT_TABLE = f'result_{NO}0k'


if __name__ == '__main__':
    tables = conn.show_tables()

    combine_tables = []
    for index in range(NO - 10, NO):
        if f'result{index}' in tables:
            combine_tables.append(f'result{index}')
    print(combine_tables)


    conn.combine_tables(OUTPUT_TABLE, combine_tables)

    conn.close()








