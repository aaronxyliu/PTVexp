import matplotlib.pyplot as plt
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import sys
import json

URL_BLACKLIST = ['menards.com']


def analyze(table_name):
    res = conn.selectAll(table_name, ['result', 'time', 'url'])
    avg_release_time_dist = Dist()


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
                date = lib['date']

                if date and len(date) >= 4:
                    avg_release_time_dist.add(libname, date)

        
    new_dist = Dist()
    for pair in avg_release_time_dist.avgDateDict().items():
        new_dist.add(pair[1][:4], pair[0])  # <year, [libnames]>

    star_dist = Dist()
    for pair in new_dist.dict.items():
        year = pair[0]
        libs = pair[1]
        i = 0
        star_sum = 0
        for libname in libs:
            res = conn2.fetchone(f"SELECT `star` FROM `libs_cdnjs` WHERE `libname`='{libname}'")
            if res:
                star_sum += int(res[0])
                i += 1
        print(star_sum)
        star_dist.add(year, star_sum / i)

    star_dist.showplot('Average Star Number of Libraries with Average Release Year', processFunc=lambda x:x[0], xlabel='year', ylabel='# avg. star')


analyze('result03')