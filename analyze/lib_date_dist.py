import pandas as pd
import math
import matplotlib.pyplot as plt
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
import sys
import json

URL_BLACKLIST = ['menards.com']


def analyze(table_name, web_num_limit=1000000):
    res = conn.selectAll(table_name, ['result', 'time', 'url'])

    web_cnt = 0
    lib_occurrence_cnt = 0
    lib_occur_with_date_cnt = 0
    date_dict = {}
    y2015dict = {}

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
                if date and len(date) >= 4:
                    lib_occur_with_date_cnt += 1
                    year = date[:4]
                    if year == '2015':
                        if libname not in y2015dict:
                            y2015dict[libname] = 1
                        else:
                            y2015dict[libname] += 1
                    if year not in date_dict:
                        date_dict[year] = 1
                    else:
                        date_dict[year] += 1

    # Sort by year
    date_dict = dict(sorted(date_dict.items(), key=lambda x:x[0], reverse=False))
    year_list = []
    range_list = []
    for pair in date_dict.items():
        year_list.append(pair[0])
        range_list.append(pair[1])
    print(year_list)
    print(range_list)
    logger.info(f'Website number: {web_cnt}')
    logger.info(f'Library occurrence: {lib_occurrence_cnt}')
    logger.info(f'Library occurrence with date: {lib_occur_with_date_cnt}')
    logger.info(y2015dict)

    plt.bar(x=range(len(year_list)), height=range_list, width=0.5,
            color="#F5CCCC",
            edgecolor="#C66667")

    label_list = year_list
    plt.xticks(range(len(year_list)), label_list)
    plt.xlabel("Size")
    plt.ylabel("Number")

    plt.rcParams['figure.figsize'] = [6.2, 3]
    plt.show()

if __name__ == '__main__':
    # Usage: python3 analyze/lib_date_dist.py result03 1000       Analyze the table 'table03' and take the front 1000 websites
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    elif len(sys.argv) == 3:
        analyze(sys.argv[1], int(sys.argv[2]))
    conn.close()