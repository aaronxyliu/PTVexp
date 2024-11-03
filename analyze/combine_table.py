
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
import pandas as pd

OUTPUT_TABLE = 'result_100k'
WEBSITE_NUM_LIMIT = 100000

COLUMNS = ['rank', 'url', 'result', 'time', 'dscp', 'pageurl', 'title']

old_df = pd.read_csv('data/SEMrushRanks-us-2023-02-23.csv')
BLACKLIST = old_df['Domain'].tolist()

def updateAll():

    # WEBSITE_LIST_FILE = f'data/top-1m.17oct2024.csv'
    # df = pd.read_csv(WEBSITE_LIST_FILE)
    # urls = df['url'].tolist()

    conn.create_new_table(OUTPUT_TABLE , '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `rank` int DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        `result` json DEFAULT NULL,
        `time` float DEFAULT NULL,
        `dscp` varchar(500) DEFAULT NULL,
        `pageurl` varchar(500) DEFAULT NULL,
        `title` varchar(1000) DEFAULT NULL,
        PRIMARY KEY (`id`)
        ''')
    
    for rank in range(1, WEBSITE_NUM_LIMIT + 1):
            
        res = conn.selectOne('result03', COLUMNS, f"`rank`='{rank}'")
        if res:
            conn.insert(OUTPUT_TABLE, COLUMNS, res)
        else:
            res2 = conn2.selectOne('result01', COLUMNS, f"`rank`='{rank}'")
            if res2:
                conn.insert(OUTPUT_TABLE, COLUMNS, res2)     
            else:
                res3 = conn2.selectOne('result02', COLUMNS, f"`rank`='{rank}'")
                if res3:
                    conn.insert(OUTPUT_TABLE, COLUMNS, res3)           
                else:
                    logger.warning(f'{rank}: no results found.')


    logger.info('Complete.')


if __name__ == '__main__':
    updateAll()

    conn.close()
    conn2.close()








