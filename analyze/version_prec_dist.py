# Check the version precision detected by PTV

import ultraimport
globalv = ultraimport('__dir__/../utils/globalv.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution


import json
import numpy as np

SUFFIX = '200k'
TABLE_NAME = f'result_{SUFFIX}'
WEBS_NUM_LIMIT = 10
EXCLUDE_FRAMEWORKS = True

def analyze():
    release_num_dict = globalv.releaseNumInfo()

    
    i = 0
    no_zero_libs_cnt = 0
    error_cnt = 0
    unknown_but_acceptable_num = 0

    version_dist = Dist()

    web_tables = conn.show_tables()
    for table_name in globalv.WEB_DATASET:
        if table_name not in web_tables:
            continue

        logger.info(f'Analyzing the detection result table {table_name}...')
        res = conn.selectAll(table_name, ['rank', 'result', 'time'])
        for entry in res:
            i += 1
            # if i > WEBS_NUM_LIMIT:
            #     break
            rank = entry[0]
            time = entry[0]
            if time < 0:
                # Error
                continue    

            libs = json.loads(entry[1])
            if libs:
                if isinstance(libs, str):
                    libs = json.loads(libs)

                if isinstance(libs, dict):
                    # Convert dictionary to list    example: https://kuruma-ex.jp/
                    new_libs = []
                    for _, val in libs.items():
                        new_libs.append(val)
                    libs = new_libs

                if len(libs) > 400:
                    error_cnt += 1
                    # Detection error
                    continue

                if len(libs) > 0:
                    no_zero_libs_cnt += 1

                for lib in libs:
                    libname = lib['libname']

                    if EXCLUDE_FRAMEWORKS and libname in globalv.FRAMEWORKS:
                        continue

                    versions = lib['version']
                    v_num = len(versions)
                    if v_num == 0:
                        if not release_num_dict[libname]:
                            continue
                        if release_num_dict[libname] <= 10:
                            unknown_but_acceptable_num += 1
                        v_num = release_num_dict[libname]
                        
                    version_dist.add(v_num, rank)

    logger.custom('Zero Libs Count', len(res) - no_zero_libs_cnt - error_cnt)
    lib_num = version_dist.size()
    logger.custom('Library Number', lib_num)
    logger.custom('Acceptable', unknown_but_acceptable_num)
    freq_dict = version_dist.freqDict()
    logger.info(freq_dict)
    sum = 0
    for i in range(1, 11):
        sum += freq_dict[i]
    # logger.info(f"1: {freq_dict['1']} ({round(freq_dict['1'] * 100 / lib_num)}%)")
    # logger.info(f"2: {freq_dict['2']}({round(freq_dict['2'] * 100 / lib_num)}%)")
    # logger.info(f"3: {freq_dict['3']}({round(freq_dict['3'] * 100 / lib_num)}%)")
    # logger.info(f"4: {freq_dict['4']}({round(freq_dict['4'] * 100 / lib_num)}%)")
    # logger.info(f"5: {freq_dict['5']}({round(freq_dict['5'] * 100 / lib_num)}%)")
    # left_no = lib_num - freq_dict['1'] - freq_dict['2'] - freq_dict['3'] - freq_dict['4'] - freq_dict['5']
    logger.info(f'<= 10: {sum}({round(sum * 100 / lib_num)}%)')
    version_dist.showplot(f'Version Range Size Distribution on {TABLE_NAME}', xlabel='version range size', ylabel='frequence', sortByX=True)


    
if __name__ == '__main__':
    analyze()
    logger.timecost()
    conn.close()
