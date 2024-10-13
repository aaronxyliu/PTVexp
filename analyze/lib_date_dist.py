import matplotlib.pyplot as plt
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import sys
import json

URL_BLACKLIST = ['menards.com']


def analyze(table_name, web_num_limit=1000000):
    res = conn.selectAll(table_name, ['result', 'time', 'url'])

    web_cnt = 0
    lib_occurrence_cnt = 0
    lib_occur_with_date_cnt = 0
    lib_occur_with_version = 0
    y2015dist = Dist()
    date_dist = Dist()
    avg_release_time_dist = Dist()
    no_version_libs = Dist()
    lib_dist = Dist()
    lib_date_dist = Dist()

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

                lib_dist.add(libname)

                if version and len(version) > 0:
                    lib_occur_with_version += 1
                else:
                    no_version_libs.add(libname, url)

                if date and len(date) >= 4:
                    lib_date_dist.add(date[:4], libname)
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
    logger.info(y2015dist.freqDict('Libraries Released in 2015'))
    # logger.info(no_version_libs.freqDict('Libraries with no version'))
    logger.info(avg_release_time_dist.avgDateDict('Average Release Time of Each Library'))
    # lib_dist.showplot('Most Frequently Used Libraries', xlabel='library', ylabel='# occurrences', sortByFreq=True, head=20)
    # lib_date_dist.showplot('Library Occurrence Release Time Distribution', xlabel='year', ylabel='# library occurrences')
    date_dist.showplot('Library Release Year Distribution on Top 10k Websites', xlabel='year', ylabel='# library occurrences')
    # new_dist = Dist()
    # for pair in avg_release_time_dist.avgDateDict().items():
    #     new_dist.add(pair[1][:4])
    # new_dist.showplot('Library Average Release Time Distribution', xlabel='year', ylabel='# libraries')
        


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