import matplotlib.pyplot as plt
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
Dist2 = ultraimport('__dir__/../utils/stat.py').Distribution2

import sys
import json

URL_BLACKLIST = ['menards.com']


def analyze(table_name, web_num_limit=1000000):
    res = conn.selectAll(table_name, ['result', 'time', 'url'])

    web_cnt = 0
    lib_occurrence_cnt = 0
    lib_occur_with_date_cnt = 0
    lib_occur_with_version = 0
    y2015dist = Dist('Libraries Released in 2015')

    date_dist = Dist('Release Date Distribution of Detected Libraries')

    avg_release_time_dist = Dist2('Average Release Time of Each Library')

    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue
        url = entry[2]
        if url in URL_BLACKLIST:
            continue

        web_cnt += 1
        if web_cnt > web_num_limit:
            break
        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                libname = lib['libname']
                lib_occurrence_cnt += 1
                date = lib['date']
                version = lib['version']
                if version and len(version) > 0:
                    lib_occur_with_version += 1
                if date and len(date) >= 4:
                    avg_release_time_dist.add(libname, date)

                    lib_occur_with_date_cnt += 1
                    year = date[:4]
                    if year == '2015':
                        y2015dist.add(libname)
                    date_dist.add(year)

    logger.info(f'Website number: {web_cnt}')
    logger.info(f'Library occurrence: {lib_occurrence_cnt}')
    logger.info(f'Library occurrence with version: {lib_occur_with_version}')
    logger.info(f'Library occurrence with date: {lib_occur_with_date_cnt}')
    logger.info(y2015dist)
    logger.info(avg_release_time_dist)
    new_dist = Dist('Library Average Release Time Distribution')
    for pair in avg_release_time_dist.average_dict.items():
        new_dist.add(pair[1][:4])
    new_dist.showplot()
        


    # date_dist.showplot()

if __name__ == '__main__':
    # Usage: python3 analyze/lib_date_dist.py result03 1000       Analyze the table 'table03' and take the front 1000 websites
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    elif len(sys.argv) == 3:
        analyze(sys.argv[1], int(sys.argv[2]))
    conn.close()