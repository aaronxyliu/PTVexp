
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
import pandas as pd
import sys

WEBSITE_LIST_FILE = 'data/SEMrushRanks-us-2023-02-23.csv'

opt = webdriver.ChromeOptions()
opt.add_extension(f'bin/PTV.crx')
service = webdriver.ChromeService(executable_path="./bin/chromedriver")
driver = webdriver.Chrome(service=service, options=opt)


def retrieveInfo(url):
    try:
        driver.get("http://" + url)
    except Exception as e:
        logger.warning(e)
        return '[]', '-1'   # web loading failed
    
    try:
        WebDriverWait(driver, timeout=30).until(presence_of_element_located((By.XPATH, '//meta[@id="lib-detect-result" and @content]')))
    except Exception as e:
        logger.warning(e)

        # Restart the driver
        driver.quit()
        driver = webdriver.Chrome(service=service, options=opt)

        return '[]', '-1'   # detection timeout
    
    result_str = driver.find_element(By.XPATH, '//*[@id="lib-detect-result"]').get_attribute("content")
    detect_time = driver.find_element(By.XPATH, '//*[@id="lib-detect-time"]').get_attribute("content")

    return result_str, detect_time

def updateAll(table_name, start_no = 0):
    conn.create_if_not_exist(table_name, '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `rank` int DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        `result` json DEFAULT NULL,
        `time` float DEFAULT NULL,
        PRIMARY KEY (`id`)
        ''')
    
    df = pd.read_csv(WEBSITE_LIST_FILE)
    for i in range(df.shape[0]):
        if i < start_no:
            continue
        rank = df.loc[i, 'Rank']
        url = df.loc[i, 'Domain']
        result_str, detect_time = retrieveInfo(url)
        conn.insert(table_name\
            , ['rank', 'url', 'result', 'time']\
            , (rank, url, result_str, detect_time))
    
        logger.info(f'{url} finished. ({i} / {df.shape[0]})')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        logger.info('Need provide the output table name.')
    elif len(sys.argv) == 2:
        updateAll(sys.argv[1])
    elif len(sys.argv) == 3:
        updateAll(sys.argv[1], int(sys.argv[2]))
    else:
        updateAll()
    driver.quit()
    conn.close()








