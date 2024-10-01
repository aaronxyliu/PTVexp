import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import sys
import json
import numpy as np


def average_date(dates: list) -> str:
    if not dates or len(dates) == 0:
        return ''
    mean_date = (np.array(dates, dtype='datetime64[s]')
                        .view('i8')
                        .mean()
                        .astype('datetime64[s]'))
    return str(mean_date)[:10]

def analyze(table_name):
    res = conn.selectAll(table_name, ['result', 'time', 'id'])
    lib_tablename_list = conn2.show_tables()

    no_match_dist = Dist()
    no_release_dist = Dist()

    lib_cnt = 0
    version_cnt = 0

    case1 = 0
    case2 = 0
    case3 = 0
    case4 = 0

    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue

        libs = json.loads(entry[0])
        id = entry[2]
        if libs:
            for lib in libs:
                libname = lib['libname']
                lib_cnt += 1
                lib['date'] = ''
                if libname not in lib_tablename_list:
                    logger.warning(f'{libname} has no data in the Releases database.')
                    no_release_dist.add(libname)
                    continue
                
                res2 = conn2.fetchall(f"SELECT `tag_name`, `publish_date` FROM `{libname}` ORDER BY `publish_date` DESC;")
                if len(res2) == 0:
                    logger.warning(f'{libname} is empty in the Releases database.')
                    no_release_dist.add(libname)
                    continue

                versions = lib['version']
                date_list = []
                for version in versions:
                    version_cnt += 1
                    match_flag = False

                    previous_entry = None
                    for entry2 in res2:
                        if SV(entry2[0]) < SV(version):
                            if not previous_entry:
                                # This version is newer than all
                                date_list.append(entry2[1])
                                case1 += 1
                            else:
                                # This version is between two entries
                                date_list.append(average_date([previous_entry[1], entry2[1]]))
                                case2 += 1
                            match_flag = True
                            break
                        elif SV(entry2[0]) == SV(version):
                            # The version matches
                            date_list.append(entry2[1])
                            match_flag = True
                            case3 += 1
                            break
                        previous_entry = entry2

                    if not match_flag:
                        # This version is older than all
                        if SV(version) < SV(previous_entry[0]):
                            case4 += 1
                        else:
                            no_match_dist.add(libname)
                
                # Take the average release date
                lib['date'] = average_date(date_list)

            conn.update(table_name, ['result'], (json.dumps(libs),), f"`id`='{id}'")

        logger.info(f'{id} finished.')
    logger.info(f'# Libs: {lib_cnt}')
    logger.info(f'# Versions: {version_cnt}')
    logger.info(f'# Libs no release date: {no_release_dist.size()}')
    logger.info(f'# Newest: {case1}')
    logger.info(f'# Between: {case2}')
    logger.info(f'# Exact match: {case3}')
    logger.info(f'# Oldest: {case4}')
    logger.info(f'# Versions no release date: {no_match_dist.size()}')

    logger.info(no_release_dist.freqDict('No Release Time Match Libraries'))
    logger.info(no_match_dist.freqDict("NO VERSION INFO IN DATABASE 'RELEASES'"))

    

                
                

                            





if __name__ == '__main__':
    # Usage: python3 analyze/lib_release_time_induce.py result03
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    conn.close()
    conn2.close()