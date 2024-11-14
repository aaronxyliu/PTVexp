import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np

TABLE_NAME = 'result_200k'

def analyze():
    res = conn.selectAll(TABLE_NAME, ['rank', 'time', 'dscp'])
    response_dist = Dist()

    i = 0
    other_dict = {}
    for entry in res:
        i += 1
        rank = entry[0]
        time = entry[1]
        dscp = entry[2]
        

        if time != -1:
            response_dist.add('success', rank)
        elif '404' in dscp:
            response_dist.add('404', rank)
        elif '403' in dscp:
            response_dist.add('403', rank)
        elif 'privacy' in dscp:
            response_dist.add('privacy', rank)
        elif 'timeout' in dscp or 'web loading failed' in dscp:
            response_dist.add('timeout', rank)
        elif 'just a moment' in dscp:
            response_dist.add('human verify', rank)
        else:
            response_dist.add('server error', rank)
            other_dict[rank] = dscp
    # print(other_dict)
    response_dist.showplot('The responsiveness and reported HTTP status code across the lists.', xlabel='type', ylabel='# webs')


if __name__ == '__main__':
    analyze()
    logger.timecost()
    conn.close()
