import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
import sys
import json

URL_BLACKLIST = ['menards.com']

def analyze(table_name):
    res = conn.selectAll(table_name, ['result', 'time', 'url'])

    web_cnt = 0
    lib_dict = {}
    lib_no_version_dict = {}        # Libraries without version information
    lib_cnt = 0
    lib_with_version_cnt = 0

    

    underscore_versions = []

    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue
        url = entry[2]
        if url in URL_BLACKLIST:
            continue
        web_cnt += 1
        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                libname = lib['libname']
                version = lib['version']

                if libname == 'medium-editor':
                    underscore_versions .append(version)



                
                if libname not in lib_dict:
                    lib_dict[libname] = 1
                else:
                    lib_dict[libname] += 1
                lib_cnt += 1
                if version and len(version) > 0:
                    lib_with_version_cnt += 1
                else:
                    if libname not in lib_no_version_dict:
                        lib_no_version_dict[libname] = 1
                    else:
                        lib_no_version_dict[libname] += 1

    # Sort by frequency from large to small
    sorted_dict = dict(sorted(lib_dict.items(), key=lambda x:x[1], reverse=True))
    sorted_dict2 = dict(sorted(lib_no_version_dict.items(), key=lambda x:x[1], reverse=True))
    logger.info(f'Website number: {web_cnt}')
    logger.info(f'Library number: {len(sorted_dict)}')
    logger.info(f'Library occurrence: {lib_cnt}')
    logger.info(f'Library occurrence with version number: {lib_with_version_cnt} ({round(lib_with_version_cnt*100/lib_cnt)}%)')

    logger.info("\n ==== Library Frequency Ranking ====")
    logger.info(sorted_dict)

    logger.info("\n ==== No Version Information Library Frequency Ranking ====")
    logger.info(sorted_dict2)

    logger.info('== underscore ==')
    logger.info(underscore_versions)


if __name__ == '__main__':
    # Usage: python3 analyze/lib_dist.py result03
    if len(sys.argv) == 1:
        logger.info('Need provide the detection result table name.')
    elif len(sys.argv) == 2:
        analyze(sys.argv[1])
    conn.close()
    logger.close()