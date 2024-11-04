import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Scatter = ultraimport('__dir__/../utils/stat.py').Scatter

import sys
import json
import math
import pandas as pd

URL_BLACKLIST = []
LIB_STAT_TABLE = 'libs_100k'
RANK_SAVE_PATH = 'data/LibRank/'

def calRankList(l):
    return  [sorted(l, reverse=True).index(x)+1 for x in l]

def analyze():
    res = conn.selectAll(LIB_STAT_TABLE, ['starrank', 'avg. date', '# loaded', 'star'])
    starlist = []
    starranklist = []
    datelist = []
    loadedlist = []
    
    for entry in res:
        starranklist.append(entry[0])
        datelist.append(entry[1])
        loadedlist.append(entry[2])
        starlist.append(entry[3])
    
    loadedranks = calRankList(loadedlist)
    # Scatter(starlist, loadedlist).plot(xlabel='star', ylabel='# loaded', yrange=[0, 10000])
    # Scatter(starranklist, loadedlist).plot(xlabel='starrank', ylabel='# loaded', yrange=[1000, 10000])
    # Scatter(starranklist, loadedranks).plot(xlabel='starrank', ylabel='# loaded rank')

    # Scatter(starranklist, datelist).plot(xlabel='starrank', ylabel='avg. date', dateY=True, yrange=['2010-01-01','2025-01-01'])
    Scatter(loadedranks, datelist).plot(xlabel='# loaded rank', ylabel='avg. date', dateY=True, yrange=['2010-01-01','2025-01-01'])

if __name__ == '__main__':

    analyze()
    conn.close()
    logger.close()