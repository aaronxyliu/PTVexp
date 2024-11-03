
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
import pandas as pd
import sys
import json
import multiprocessing
import time

# http://hpdns.net/
old_df = pd.read_csv('data/SEMrushRanks-us-2023-02-23.csv')
BLACKLIST = old_df['Domain'].tolist()

def retrieveInfo(driver, url):
    logger.info(f"Retrieving {url}")
    try:
        driver.get("http://" + url)
    except Exception as e:
        logger.warning(e)
        return '[]', -1, 'web loading failed', '', ''   # web loading failed
    
    cur_url = ''
    try:
        cur_url = driver.current_url
    except:
        pass
    if cur_url == None:
        cur_url = ''
    
    webTitle = ''
    try:
        # The selenium title fetching is not stable
        webTitle = driver.title
        webtitle = str.lower(driver.title)
        print(webtitle)
        if '404' in webtitle or '403' in webtitle or 'error' in webtitle:
            logger.warning(f'Page blocked: {webtitle}.')
            return '[]', -1, f'Page blocked: {webtitle}', cur_url, webTitle
        elif 'just a moment...' in webtitle:
            logger.warning(f'Human verification required: {webtitle}.')
            return '[]', -1, f'Human verification required: {webtitle}', cur_url, webTitle
    except:
        pass
    
    try:
        WebDriverWait(driver, timeout=20).until(presence_of_element_located((By.XPATH, '//meta[@id="lib-detect-result" and @content]')))
    except Exception as e:
        logger.warning(e)

        # Restart the driver
        driver.quit()
        driver.start_client()

        return '[]', -1, 'detection timeout', cur_url, webTitle   # detection timeout
    
    result_str = driver.find_element(By.XPATH, '//*[@id="lib-detect-result"]').get_attribute("content")
    detect_time_str = driver.find_element(By.XPATH, '//*[@id="lib-detect-time"]').get_attribute("content")
    detect_time = float(detect_time_str)

    return result_str, detect_time, '', cur_url, webTitle

def ExistUnknown(table_name: str, url: str) -> bool:
    res = conn.fetchone(f"SELECT `result` FROM {table_name} WHERE `url`='{url}'")
    if not res:
        return True
    libs = json.loads(res[0])
    if not libs or len(libs) == 0:
        return True
    for lib in libs:
        version = lib['version']
        if not version and len(version) == 0:
            return True
        
    return False

def updateAll(df, table_name, start_no = 0, channel = None):
    conn.create_if_not_exist(table_name, '''
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
    website_num = df.shape[0]
    i = 0
    while True:
        opt = webdriver.ChromeOptions()
        opt.add_extension(f'bin/PTV.crx')
        service = webdriver.ChromeService(executable_path="./bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=opt)
        driver.set_page_load_timeout(20)

        while True:
            if i < start_no:
                i += 1
                continue
            if i >= website_num:
                break
            
            rank = df.loc[i, 'rank']
            url = df.loc[i, 'url']

            if channel:
                channel['heartbeat_time'] = time.time()
                channel['start_no'] = i
            
            if url in BLACKLIST:
                i += 1
                continue

            # if not ExistUnknown(table_name, url):
            #     continue

            result_str, detect_time, exception, pageurl, title = retrieveInfo(driver, url)
            conn.update_otherwise_insert(table_name\
                , ['rank', 'result', 'time', 'dscp', 'pageurl', 'title']\
                , (rank, result_str, detect_time, exception, pageurl[:400], title[:900])\
                , 'url', url)
        
            
            logger.info(f'{url} finished. ({i} / {website_num})')
            
            i += 1
            if detect_time < 0:
                # Restart the driver if error appears
                break
            

        driver.quit()
        if i >= website_num:
            break

if __name__ == '__main__':
    # Usage: python3 exp/ext_test.py result04 0    "result03" is the table name  "0" is the start number
    if len(sys.argv) != 3:
        logger.info('Need provide the output table name and the start number.')

    channel = multiprocessing.Manager().dict()  # Communication Channel
    channel['heartbeat_time'] = time.time()
    channel['start_no'] = int(sys.argv[2])

    category = sys.argv[1]
    WEBSITE_LIST_FILE = f'data/top-1m.17oct2024.csv'
    df = pd.read_csv(WEBSITE_LIST_FILE)
    website_num = df.shape[0]

    
    p = multiprocessing.Process(target=updateAll, args=(df, category, int(sys.argv[2]), channel))
    p.start()

    while True:
        time.sleep(4)  # Check the heartbeat every 4 seconds
        if not p.is_alive():
            break
        time_delta = time.time() - channel['heartbeat_time']
        print(time_delta)

        if time_delta > 45:
            # The heartbeat interval is larger than 45 seconds
            logger.info(f"Process timeouts. Skip this page.")
            channel['start_no'] += 1
            p.terminate()

            time.sleep(1) # waiting for the process termination complete
            p.close()   # release resources
            channel['heartbeat_time'] = time.time()
            
            p = multiprocessing.Process(target=updateAll, args=(df, category, channel['start_no'], channel))
            p.start()
        if channel['start_no'] >= website_num:
            break

    if p.is_alive():
        p.terminate()
    conn.close()








