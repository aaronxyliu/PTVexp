
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
import pandas as pd

OUTPUT_TABLE = 'result_1M'
WEBSITE_NUM_LIMIT = 100000


if __name__ == '__main__':
    conn2.combine_tables(OUTPUT_TABLE, ['result90', 'result92', 'result95', 'result98'])

    conn.close()
    conn2.close()








