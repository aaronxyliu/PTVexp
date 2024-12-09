import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
globalv = ultraimport('__dir__/../utils/globalv.py')
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion

import sys
import json
import math

URL_BLACKLIST = []

def analyze(libname, version):
    libs_with_version = Dist()
    libs_with_other_versions = Dist()
    with_version_num = 0
    with_other_versions_num = 0

    web_tables = conn.show_tables()
    for table_name in globalv.WEB_DATASET:
        if table_name not in web_tables:
            continue
        logger.info(f'Analyzing the detection result table {table_name}...')
        res = conn.selectAll(table_name, ['result', 'time', 'url', 'rank'])



        for entry in res:
            time = entry[1]
            url = entry[2]
            rank = entry[3]
            if time < 0:
                # Error
                continue
            if url in URL_BLACKLIST:
                continue
            libs = json.loads(entry[0])

            if libs:
                if len(libs) > 300:
                        # Detection error
                        continue
                for lib in libs:
                    versions = lib['version']
                    if lib['libname'] == libname:
                        if len(versions) > 0 and SV(versions[0]) == SV(version):
                            with_version_num += 1
                            for otherlib in libs:
                                if otherlib['libname'] != libname:
                                    libs_with_version.add(otherlib['libname'])
                        else:
                            with_other_versions_num += 1
                            for otherlib in libs:
                                if otherlib['libname'] != libname:
                                    libs_with_other_versions.add(otherlib['libname'])
                        break
        
    freq_dict1 = {}
    for pair in libs_with_version.freqDict().items():
        freq_dict1[pair[0]] = pair[1] / with_version_num
    freq_dict2 = {}
    for pair in libs_with_other_versions.freqDict().items():
        freq_dict2[pair[0]] = pair[1] / with_other_versions_num

    diff_dict = {}
    for pair in freq_dict1.items():
        diff_dict[pair[0]] = pair[1] - freq_dict2.get(pair[0], 0)  # get(key, 0) returns 0 if not found
    for pair in freq_dict2.items():
        if pair[0] not in diff_dict:
            diff_dict[pair[0]] = -pair[1]
    
    diff_dict = dict(sorted(diff_dict.items(), key=lambda x:x[1], reverse=True))
    logger.custom(f'Distribution Difference of other libraries on {libname} {version} (TOP)', dict(list(diff_dict.items())[:10]))
    logger.custom(f'Distribution Difference of other libraries on {libname} {version} (BOTTOM)', dict(list(diff_dict.items())[-10:]))


if __name__ == '__main__':
    # Usage: python3 analyze/inquery_version.py jquery 1.12.4
    if len(sys.argv) < 3:
        logger.info('Need provide the library name and a specific version.')
    elif len(sys.argv) == 3:
        analyze(sys.argv[1], sys.argv[2])
    conn.close()
    logger.close()