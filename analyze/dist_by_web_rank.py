import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np

# URL_BLACKLIST = ['menards.com']


def analyze(table_name, lib_blacklist):
    res = conn.selectAll(table_name, ['rank', 'result', 'time', 'url'])
    avg_release_time_dist = Dist()
    freq_dist = Dist()
    diversity_dist = Dist()


    for entry in res:
        time = entry[2]
        if time < 0:
            # Error
            continue
        rank = entry[0]

        libs = json.loads(entry[1])
        if libs:
            in_blacklist = 0
            for lib in libs:
                libname = lib['libname']
                if libname in lib_blacklist:
                    in_blacklist += 1
                    continue
                diversity_dist.add(rank, libname)

                if 'date' not in lib:
                    continue
                date = lib['date']
                if date and len(date) >= 4:
                    avg_release_time_dist.add(rank, date)
            freq_dist.add(rank, len(libs) - in_blacklist)
    
    # avg_release_time_dist.showplot('Average Date of Libraries of Different Web Ranks', xlabel='rank', ylabel='avg. date', partition=20, processFunc=avg_release_time_dist.avgYear, yrange=[2010,2025])
    freq_dist.showplot('Average Libraries of Each Web Ranks', xlabel='rank', ylabel='avg. # of loaded libs', partition=15, processFunc=lambda x:np.mean(x))
    # diversity_dist.showplot('Number of Different Libraries Used by Each Web Ranks', xlabel='rank', ylabel='# libraries', partition=15, processFunc=lambda x:len(set(x)))



def mask(percent, reverse=False):
    res = conn2.selectAll('libs', ['library', 'starrank', 'star'])
    lib_blacklist = []
    lib_num = len(res)
    for entry in res:
        if entry[2] == 0:
            continue
        if not reverse and entry[1] <= lib_num * percent:
            lib_blacklist.append(entry[0])
        elif reverse and entry[1] >= lib_num * percent:
            lib_blacklist.append(entry[0])
    return lib_blacklist

lib_blacklist = mask(0.6)
analyze('result05', lib_blacklist)