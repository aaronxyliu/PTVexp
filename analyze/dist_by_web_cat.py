import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection2')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np

# URL_BLACKLIST = ['menards.com']


def analyze(lib_blacklist=[]):
    tables = conn.show_tables()
    avg_release_time_dist = Dist()
    freq_dist = Dist()
    diversity_dist = Dist()

    for table_name in tables:
        res = conn.selectAll(table_name, ['result', 'time', 'url'])
        for entry in res:
            time = entry[1]
            if time < 0:
                # Error
                continue

            libs = json.loads(entry[0])
            if libs:
                in_blacklist = 0
                for lib in libs:
                    libname = lib['libname']
                    if libname in lib_blacklist:
                        in_blacklist += 1
                        continue
                    diversity_dist.add(table_name, libname)

                    if 'date' not in lib:
                        continue
                    date = lib['date']
                    if date and len(date) >= 4:
                        avg_release_time_dist.add(table_name, date)
                freq_dist.add(table_name, len(libs) - in_blacklist)
    
    avg_release_time_dist.showplot('Average Date of Libraries of Different Web Category', xlabel='category', ylabel='avg. date', processFunc=avg_release_time_dist.avgDate, sortByY=True, dateY=True, yrange=['2010-01-01','2025-01-01'])
    # freq_dist.showplot('Average Libraries of Each Web Category', xlabel='category', ylabel='avg. # of loaded libs', processFunc=lambda x:np.mean(x), sortByY=True)
    #diversity_dist.showplot('Number of Different Libraries Used by Each Web Category', xlabel='category', ylabel='# libraries', processFunc=lambda x:len(set(x)), sortByY=True)



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

# lib_blacklist = mask(0.6)
analyze()