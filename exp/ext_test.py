
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
globalv = ultraimport('__dir__/../utils/globalv.py')


WEB_LOAD_TIMEOUT = 30
PROCESS_UNRESPONSE_TIMEOUT = 60
DETECTION_TIMEOUT = 25
SKIP_EXISTED = False
APPLY_PTV_UPDATE = False # Only detect websites containing libraries that have updates in PTV

# http://hpdns.net/
# old_df = pd.read_csv('data/SEMrushRanks-us-2023-02-23.csv')
# BLACKLIST = old_df['Domain'].tolist()
BLACKLISTRANK = [601302, 633941, 804380]
LARGE_INT = 1000000000

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
        if webTitle == None:
            webTitle = ''
        webtitle = str.lower(driver.title)
        logger.debug(f"    Title: {webtitle}")
        if '404' in webtitle or '403' in webtitle or 'error' in webtitle:
            logger.warning(f'Page blocked: {webtitle}.')
            return '[]', -1, f'Page blocked: {webtitle}', cur_url, webTitle
        elif 'just a moment...' in webtitle:
            logger.warning(f'Human verification required: {webtitle}.')
            return '[]', -1, f'Human verification required: {webtitle}', cur_url, webTitle
    except:
        pass
    
    try:
        WebDriverWait(driver, timeout=DETECTION_TIMEOUT).until(presence_of_element_located((By.XPATH, '//meta[@id="lib-detect-time" and @content]')))
    except Exception as e:
        logger.warning(e)

        # Restart the driver
        # driver.quit()
        # driver.start_client()

        return '[]', -1, 'detection timeout', cur_url, webTitle   # detection timeout
    
    try:
        result_str = driver.find_element(By.XPATH, '//*[@id="lib-detect-result"]').get_attribute("content")
    except Exception as e:
        logger.warning(e)
        return '[]', -1, 'find element error', cur_url, webTitle   # detection timeout
    
    if result_str == None or result_str == '':
        return '[]', -1, 'detection error', cur_url, webTitle   # detection timeout

    detect_time_str = driver.find_element(By.XPATH, '//*[@id="lib-detect-time"]').get_attribute("content")
    try:
        detect_time = float(detect_time_str)
    except:
        detect_time = 0

    return result_str, detect_time, '', cur_url, webTitle

def ExistUpdatedLib(table_name: str, rank: int) -> bool:
    res = conn.selectOne(table_name, ['result'], f"`rank`='{rank}'")
    if not res:
        return False
    libs = json.loads(res[0])
    if libs:
        if isinstance(libs, str):
            libs = json.loads(libs)

        if isinstance(libs, dict):
            # Convert dictionary to list    example: https://kuruma-ex.jp/
            new_libs = []
            for _, val in libs.items():
                new_libs.append(val)
            libs = new_libs
        
        for lib in libs:
            if lib['libname'] in globalv.LIBS_WITH_UPDATE:
                return True
        
    return False

def updateAll(df, table_name, start_no = 1, end_no = LARGE_INT, channel = None):
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
    i = start_no
    while True:
        opt = webdriver.ChromeOptions()
        opt.add_argument("--headless")
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    
        opt.add_argument(f'user-agent={user_agent}')
        opt.add_extension(f'bin/PTV.crx')
        opt.accept_insecure_certs = True
        service = webdriver.ChromeService(executable_path="./bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=opt)
        driver.set_page_load_timeout(WEB_LOAD_TIMEOUT)

        while True:
            if channel:
                channel['heartbeat_time'] = time.time()
                if i < channel['next_no']:
                    i = channel['next_no']
                    continue
            if i >= website_num or i >= end_no:
                break
            
            rank = df.loc[i - 1, 'rank']
            url = df.loc[i - 1, 'url']
            
            if rank in BLACKLISTRANK:
                i += 1
                continue

            if SKIP_EXISTED:
                res = conn.fetchone(f"SELECT `result` FROM {table_name} WHERE `rank`={rank}")
                if res:
                    i += 1
                    continue
            
            if APPLY_PTV_UPDATE:
                if not ExistUpdatedLib(table_name, rank):
                    i += 1
                    continue
                

            result_str, detect_time, exception, pageurl, title = retrieveInfo(driver, url)
            logger.indent()
            logger.debug(result_str)
            logger.debug(detect_time)
            logger.outdent()

            print(exception)
            conn.update_otherwise_insert(table_name\
                , ['url', 'result', 'time', 'dscp', 'pageurl', 'title']\
                , (url, result_str, detect_time, exception[:400], pageurl[:400], str(title)[:900])\
                , 'rank', rank)

            
            logger.info(f'Rank {rank}: {url} finished. Saved to the table `{table_name}`. ({round((i - start_no) * 100 / (end_no - start_no), 1)}%)')
            logger.leftTimeEstimator(end_no - i)
            
            i += 1

            if channel:
                channel['heartbeat_time'] = time.time()
                channel['next_no'] = i

            if detect_time < 0:
                # Restart the driver if error appears
                break
            

        driver.quit()
        if i >= website_num or i >= end_no:
            break

def processMonitor(table_name, start_no, end_no):
    channel = multiprocessing.Manager().dict()  # Communication Channel
    channel['heartbeat_time'] = time.time()
    channel['next_no'] = start_no
    
    WEBSITE_LIST_FILE = f'data/top-1m.17oct2024.csv'
    df = pd.read_csv(WEBSITE_LIST_FILE)
    website_num = df.shape[0]

    
    p = multiprocessing.Process(target=updateAll, args=(df, table_name, start_no, end_no, channel))
    p.start()

    while True:
        time.sleep(4)  # Check the heartbeat every 4 seconds
        if not p.is_alive():
            break
        time_delta = time.time() - channel['heartbeat_time']
        # logger.debug(f'    heartbeat: {round(time_delta, 1)}s')

        if time_delta > PROCESS_UNRESPONSE_TIMEOUT:
            # The heartbeat interval is larger than 45 seconds
            logger.warning(f"Process timeouts. Skip this page.")
            channel['next_no'] += 1
            p.terminate()

            time.sleep(1) # waiting for the process termination complete
            p.close()   # release resources
            channel['heartbeat_time'] = time.time()
            
            p = multiprocessing.Process(target=updateAll, args=(df, table_name, start_no, end_no, channel))
            p.start()
        if channel['next_no'] >= website_num or channel['next_no'] >= end_no:
            break

    if p.is_alive():
        p.terminate()


if __name__ == '__main__':
    # Usage: python3 exp/ext_test.py result04 0 1000    
    #   ("result03" is the table name,  "0" is the start number,  "1000" is the end number)
    if len(sys.argv) == 4:
        # Manurally set the testing websites rank range
        if int(sys.argv[2]) >= int(sys.argv[3]):
            logger.error('The end number should be larger than the start number.')
            exit(0)
        processMonitor(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    elif len(sys.argv) == 3:
        # Only test 1 website with specific rank
        processMonitor(sys.argv[1], int(sys.argv[2]), int(sys.argv[2]) + 1)
    elif len(sys.argv) == 2:
        table_name = f'result{sys.argv[1]}'
        table_no = int(sys.argv[1])
        start_no = table_no * 10000
        end_no = (table_no + 1) * 10000
        if table_name in conn.show_tables():
            res = conn.fetchone(f"SELECT `rank` FROM {table_name} ORDER BY `id` DESC")
            if res:
                # Start from the last end
                start_no = res[0] + 1
        
        processMonitor(table_name, start_no, end_no)
    else:
        logger.error('Need provide the output table name, the start number, and the end number.')
        exit(0)
    
    logger.timecost()
    conn.close()








