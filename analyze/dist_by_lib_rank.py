import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import sys
import json
import math
import pandas as pd

URL_BLACKLIST = []
DETECTION_RESULT_TABLE = 'result05'
RANK_SAVE_PATH = 'data/LibRank/'

def analyze():
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])
    df = pd.read_csv(f'{RANK_SAVE_PATH}/byStar.rank.csv')
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
                    star = int(df.loc[df['library']==libname, 'star'].iloc[0])
                    if star > 0:
                        rank = int(df.loc[df['library']==libname, 'rank'].iloc[0])
                        date_dist.add(rank, date)
        
    date_dist.showplot('Average Date of Libraries of Different Ranks', xlabel='rank', ylabel='avg. date', partition=10, processFunc=date_dist.avgYear, yrange=[2010,2025])

if __name__ == '__main__':

    analyze()
    conn.close()
    logger.close()