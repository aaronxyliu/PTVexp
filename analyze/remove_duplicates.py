# Check the version precision detected by PTV

import ultraimport
globalv = ultraimport('__dir__/../utils/globalv.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution


import json
import numpy as np

SUFFIX = '84'
TABLE_NAME = f'result{SUFFIX}'

def analyze():
    res = conn.selectAll(TABLE_NAME, ['rank'])
    previous_rank = -1
    for entry in res:
        if entry[0] == previous_rank:
            print('delete', entry[0])
            conn.deleteOne(TABLE_NAME, f"`rank`={entry[0]}")
        previous_rank = entry[0]

    print('Left entry number:', conn.entry_count(TABLE_NAME))

if __name__ == '__main__':
    analyze()