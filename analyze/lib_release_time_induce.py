import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
import sys
import json
import numpy as np




def analyze(table_name):
    res = conn.selectAll(table_name, ['result', 'time', 'id'])
    lib_tablename_list = conn2.show_tables()

    no_release_time_lib_cnt = 0
    lib_cnt = 0
    version_cnt = 0
    version_not_found_cnt = 0

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
                    no_release_time_lib_cnt += 1
                    continue
                
                res2 = conn2.selectAll(libname, ['tag_name', 'publish_date'])
                versions = lib['version']
                date_list = []
                for version in versions:
                    version_cnt += 1
                    match_flag = False
                    for entry2 in res2:
                        if SV(entry2[0]) == SV(version):
                            date_list.append(entry2[1])
                            match_flag = True
                            break
                    if not match_flag:
                        version_not_found_cnt += 1
                
                if len(date_list) > 0:
                    # Take the average release date
                    mean_date = (np.array(date_list, dtype='datetime64[s]')
                        .view('i8')
                        .mean()
                        .astype('datetime64[s]'))
                    lib['date'] = str(mean_date)[:10]

            
            conn.update(table_name, ['result'], (json.dumps(libs),), f"`id`='{id}'")

        logger.info(f'{id} finished.')
    logger.info(f'# Libs: {lib_cnt}')
    logger.info(f'# Versions: {version_cnt}')
    logger.info(f'# Libs no release date: {no_release_time_lib_cnt}')
    logger.info(f'# Versions no release date: {version_not_found_cnt}')
                
                

                            





if __name__ == '__main__':
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    conn.close()
    conn2.close()