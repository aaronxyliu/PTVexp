import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import sys
import json
import math
import pandas as pd

URL_BLACKLIST = []
SUFFIX = '1M'
DETECTION_RESULT_TABLE = 'result_' + SUFFIX
RANK_SAVE_TABLE = 'libs_' + SUFFIX

def analyze():
    res1 = conn2.selectAll(RANK_SAVE_TABLE, ['library', 'star', 'starrank'])
    star_dict = {}
    starrank_dict = {}
    for entry in res1:
        star_dict[entry[0]] = entry[1]
        starrank_dict[entry[0]] = entry[2]

    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])
    date_dist = Dist()

    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue
        url = entry[2]
        if url in URL_BLACKLIST:
            continue
        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                libname = lib['libname']
                if 'date' not in lib:
                    continue
                date = lib['date']
                
                if date and len(date) >= 4:
                    # Find the library rank in the dataframe
                    star = star_dict[libname]
                    if star > 0:
                        rank = starrank_dict[libname]
                        date_dist.add(rank, date)
        
    date_dist.showplot('Average Date of Libraries of Different Ranks', xlabel='rank', ylabel='avg. date', partition=10, processFunc=date_dist.avgDate, dateY=True, yrange=['2010-01-01','2025-01-01'])

if __name__ == '__main__':

    analyze()
    conn.close()
    logger.close()