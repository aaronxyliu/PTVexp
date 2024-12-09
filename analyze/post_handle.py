import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np
globalv = ultraimport('__dir__/../utils/globalv.py')
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion



def analyze(table_name):

    res = conn.selectAll(table_name, ['result', 'rank'])
    for entry in res:
        rank = int(entry[1])

        libs = json.loads(entry[0])
        flag = False
        if isinstance(libs, str):
            flag = True
            libs = json.loads(libs)
        
        if libs:
            new_libs = []
            for lib in libs:
                libname = lib['libname']
                versions = lib['version']
                if libname == 'lodash.js':
                    if len(versions) > 0 and SV(versions[0]) < SV('2.0.0'):
                        flag = True
                        continue
                elif libname == 'underscore.js':
                    if len(versions) > 0 and SV('1.100.0') < SV(versions[0]):
                        flag = True
                        continue
                elif libname == 'vue2':
                    if len(versions) > 0 and SV('2.100.0') < SV(versions[0]):
                        flag = True
                        lib['libname'] = 'vue3'
                elif libname == 'jquery-tools':
                    if len(versions) > 0 and SV('2.100.0') < SV(versions[0]):
                        flag = True
                        continue
                elif libname == 'analytics.js':
                    if len(versions) > 0 and SV('2.100.0') < SV(versions[0]):
                        flag = True
                        continue
                elif libname == 'angularjs':
                    flag = True
                    continue
                new_libs.append(lib)

        if flag:
            conn.update(table_name, ['result'], (json.dumps(new_libs),), f"`rank`={rank}")

def wrapper():
    web_tables = conn.show_tables()
    for table_name in globalv.WEB_DATASET:
        if table_name not in web_tables:
            continue

        logger.info(f'Processing the detection result table {table_name}...')
        analyze(table_name)


if __name__ == '__main__':
    wrapper()
    conn.close()
    conn2.close()