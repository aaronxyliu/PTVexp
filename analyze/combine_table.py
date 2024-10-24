
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
import pandas as pd
import sys
import json
import multiprocessing
import time

WEBSITE_NUM_LIMIT = 20000

old_df = pd.read_csv('data/SEMrushRanks-us-2023-02-23.csv')
BLACKLIST = old_df['Domain'].tolist()

def updateAll():

    WEBSITE_LIST_FILE = f'data/top-1m.17oct2024.csv'
    df = pd.read_csv(WEBSITE_LIST_FILE)
    urls = df['url'].tolist()

    conn.create_if_not_exist('result04', '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `rank` int DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        `result` json DEFAULT NULL,
        `time` float DEFAULT NULL,
        `dscp` varchar(500) DEFAULT NULL,
        PRIMARY KEY (`id`)
        ''')
    
    rank = 1
    for url in urls:
        if rank > WEBSITE_NUM_LIMIT:
            break
            
        res = conn.fetchone(f'''SELECT `result`, `time`, `dscp` FROM `result03` WHERE `url`='{url}';''')
        if res:
            conn.insert('result04', ['rank', 'url', 'result', 'time', 'dscp'], (rank, url, res[0], res[1], res[2]))
        else:
            res2 = conn2.fetchone(f'''SELECT `result`, `time`, `dscp` FROM `result01` WHERE `url`='{url}';''')
            if res2:
                conn.insert('result04', ['rank', 'url', 'result', 'time', 'dscp'], (rank, url, res2[0], res2[1], res2[2]))
            else:
                logger.warning(f'{rank}: {url} no results found.')

        logger.info(f'{rank} completes.')
        rank += 1


if __name__ == '__main__':
    updateAll()

    conn.close()
    conn2.close()








