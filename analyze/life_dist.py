import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np
globalv = ultraimport('__dir__/../utils/globalv.py')

TABLE_NAME = 'libs_cdnjs_all_12_5'

def analyze(table_name):
    res = conn.selectAll(table_name, ['cdnjs rank', 'star', 'last tag date', 'first tag date'])
    begin_date_dist = Dist()
    latest_date_dist = Dist()
    latest_date_dist2 = Dist()
    has_github_cnt = 0
    lifetime_dist = Dist()

    for entry in res:
        star = entry[1]
        if star and star > 0:
            has_github_cnt += 1
        if entry[2]:
            if str(entry[3]) == 'None':
                logger.error(f'Date Empty: {entry[0]}')
            if entry[2] < entry[3]:
                logger.error(f'Date Error: {entry[0]}')
            begin_date_dist.add(entry[0], str(entry[3]))
            latest_date_dist.add(entry[0], str(entry[2]))
            latest_date_dist2.add(int(str(entry[2])[:4]))
            lifetime_dist.add(entry[0], ((entry[2] - entry[3]).days)/365)
        
    logger.info(f'Containing Github Repo: {has_github_cnt} / {len(res)}')    

    lifetime_dist.showplot('Life Time Histogram of Libraries on Each Web Rank', ylabel='frequence', xlabel='years', processFunc=lambda x:x[0],hist=True)
    # latest_date_dist.showplot('Latest Date Histogram of Libraries on Each Web Rank', ylabel='frequence', xlabel='date', dateY=True, processFunc=lambda x:x[0],hist=True)

    freq_dict = latest_date_dist2.freqDict()
    freq_dict = dict(sorted(freq_dict.items(), key=lambda x:x[0]))
    x = list(freq_dict.keys())
    y = list(freq_dict.values())
    print(x)
    print(y)
        





if __name__ == '__main__':
    analyze(TABLE_NAME)
    conn.close()
