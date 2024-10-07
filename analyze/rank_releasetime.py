import matplotlib.pyplot as plt
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import math

import sys
import json

URL_BLACKLIST = ['menards.com']


def analyze(table_name):
    res = conn.selectAll(table_name, ['rank', 'result', 'time', 'url'])
    avg_release_time_dist = Dist()


    for entry in res:
        time = entry[2]
        if time < 0:
            # Error
            continue
        url = entry[3]
        if url in URL_BLACKLIST:
            continue

        libs = json.loads(entry[1])
        if libs:
            for lib in libs:
                libname = lib['libname']
                if libname == 'jquery' or libname == 'core-js':
                    continue
                date = lib['date']

                rank_base = math.floor(float(entry[0])/1000)

                if date and len(date) >= 4:
                    avg_release_time_dist.add(f'{rank_base}k ~ {rank_base+1}k', date)
        
    logger.info(avg_release_time_dist.avgDateDict('The Relationship between Average Library Release Time and Website Rnak'))


analyze('result03')