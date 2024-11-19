import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import sys
import json
import numpy as np
import math

SUPPLEMENT_MODE = False

START_RANK = 102372


def average_date(dates: list) -> str:
    if not dates or len(dates) == 0:
        return ''
    mean_date = (np.array(dates, dtype='datetime64[s]')
                        .view('i8')
                        .mean()
                        .astype('datetime64[s]'))
    return str(mean_date)[:10]

def analyze(table_name):

    logger.info(f'Generating the quick look-up dictionary for the Releases database...')
    average_date_dict = {}
    lib_tablename_list = conn2.show_tables()
    for l in lib_tablename_list:
        res0 = conn2.fetchall(f"SELECT `publish_date` FROM `{l}` ORDER BY `publish_date` DESC;")
        dates = []
        for entry in res0:
            dates.append(entry[0])
        average_date_dict[l] = average_date(dates)

    logger.info(f'Analyzing the detection result table {table_name}...')
    res = conn.selectAll(table_name, ['result', 'time', 'rank'])

    no_match_dist = Dist()

    lib_cnt = 0
    version_cnt = 0

    case1 = 0
    case2 = 0
    case3 = 0
    case4 = 0

    # old_rank = 0
    i = 0
    for entry in res:
        i += 1
        time = entry[1]
        if time < 0:
            # Error
            continue

        libs = json.loads(entry[0])
        rank = entry[2]

        if rank < START_RANK:
            continue

        
        if libs:
            if isinstance(libs, str):
                libs = json.loads(libs)

            if isinstance(libs, dict):
                # Convert dictionary to list    example: https://kuruma-ex.jp/
                new_libs = []
                for _, val in libs.items():
                    new_libs.append(val)
                libs = new_libs
                
            for lib in libs:
                if SUPPLEMENT_MODE and 'date' in lib and lib['date']!='':
                    continue

                # Cannot encode object to json successfully on some websites:
                # https://itaucorretora.com.br/
                libname = lib['libname'] 

                lib_cnt += 1

                lib['date'] = ''
                
                if libname not in lib_tablename_list:
                    logger.warning(f'{libname} has no data in the Releases database.')
                    continue
                
                res2 = conn2.fetchall(f"SELECT `tag_name`, `publish_date` FROM `{libname}` ORDER BY `publish_date` DESC;")
                if len(res2) == 0:
                    logger.warning(f'{libname} is empty in the Releases database.')
                    continue

                versions = lib['version']
                version_cnt += 1
                if len(versions) == 0:
                    # The version prediction is "universe"
                    lib['estimated_date'] = True
                    lib['date'] = average_date_dict[libname]
                    lib['estimated_dist'] = True
                    lib['dist'] = int(len(res2)/2)
                else:
                    if len(versions) > 10:
                        lib['estimated_date'] = True
                    if len(versions) > len(res2)/3:
                        lib['estimated_dist'] = True

                    middle_version = versions[math.floor(len(versions)/2)]
                    match_flag = False
                    previous_entry = None
                    distance = 0
                    for entry2 in res2:
                        if SV(entry2[0]) == SV(middle_version):
                            # The version matches
                            lib['date'] = str(entry2[1])
                            lib['dist'] = distance
                            case3 += 1
                            match_flag = True
                            break
                        elif SV(entry2[0]) < SV(middle_version):
                            if not previous_entry:
                                # This version is newer than all
                                lib['date'] = str(entry2[1])
                                lib['dist'] = distance
                                case1 += 1
                            else:
                                # This version is between two entries
                                lib['date'] = average_date([previous_entry[1], entry2[1]])
                                lib['dist'] = distance
                                case2 += 1
                            match_flag = True
                            break
                        previous_entry = entry2
                        distance += 1

                    if not match_flag:
                        if SV(middle_version).onlySuffix():
                            # The version is only suffix, no version number, so give an estimated date
                            lib['estimated_date'] = True
                            lib['date'] = average_date_dict[libname]
                            lib['estimated_dist'] = True
                            lib['dist'] = int(len(res2)/2)
                            no_match_dist.add(libname)
                        else:
                            # This version is older than all
                            lib['date'] = str(res2[-1][1])
                            lib['dist'] = len(res2)
                            case4 += 1
            conn.update(table_name, ['result'], (json.dumps(libs),), f"`rank`={rank}")

        logger.leftTimeEstimator(len(res) - i)


    logger.info(f'# Libs: {lib_cnt}')
    logger.info(f'# Versions: {version_cnt}')
    logger.info(f'# Newest: {case1}')
    logger.info(f'# Between: {case2}')
    logger.info(f'# Exact match: {case3}')
    logger.info(f'# Oldest: {case4}')
    logger.info(f'# Versions no release date: {no_match_dist.size()}')

    logger.info(no_match_dist.freqDict("NO VERSION INFO IN DATABASE 'RELEASES'"))
   


if __name__ == '__main__':
    # Usage: python3 analyze/lib_release_time_induce.py result_200k
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    logger.timecost()
    conn.close()
    conn2.close()