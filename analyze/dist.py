import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np

URL_BLACKLIST = ['partyrock.aws']
WEBSITE_RANK_RANGE = (45 * 10000, 50 * 10000)
SUFFIX = '500k'
DETECTION_RESULT_TABLE = 'result_' + SUFFIX

def analyze(table_name, lib_blacklist):
    res = conn.selectAll(table_name, ['rank', 'result', 'time', 'url'])
    avg_release_time_dist = Dist()
    freq_dist = Dist()
    web_date_dist = Dist()
    diversity_dist = Dist()

    i = 0
    for entry in res:
        i += 1
        time = entry[2]
        if time < 0:
            # Error
            continue
        rank = int(entry[0])
        if rank < WEBSITE_RANK_RANGE[0] or rank > WEBSITE_RANK_RANGE[1]:
            continue

        if entry[3] in URL_BLACKLIST:
            continue

        libs = json.loads(entry[1])
        if libs:
            if len(libs) > 300:
                # Detection error
                continue
            in_blacklist = 0
            dates = []
            for lib in libs:
                libname = lib['libname']
                if libname in lib_blacklist:
                    in_blacklist += 1
                    continue
                diversity_dist.add(rank, libname)

                if 'date' not in lib:
                    continue
                date = lib['date']
                if date and len(date) >= 4:
                    avg_release_time_dist.add(rank, date)
                    dates.append(date)
            if len(dates) > 0:
                web_date_dist.add(rank, web_date_dist.avgDate(dates))
            freq_dist.add(rank, len(libs) - in_blacklist)
        logger.leftTimeEstimator(len(res) - i)
    # avg_release_time_dist.showplot('Average Date of Libraries of Different Web Ranks', xlabel='rank', ylabel='avg. date', partition=20, processFunc=avg_release_time_dist.avgDate, dateY=True, yrange=['2010-01-01','2025-01-01'])
    # freq_dist.showplot('Average Loaded Libraries Number on Each Web Rank', xlabel='rank', ylabel='avg. # of loaded libs', partition=15, processFunc=lambda x:np.mean(x))
    # diversity_dist.showplot('Number of Different Libraries Used by Each Web Rank', xlabel='rank', ylabel='# libraries', partition=15, processFunc=lambda x:len(set(x)))
    logger.custom('freq mean', freq_dist.mean(processFunc=lambda x:x[0]))
    logger.custom('freq variance', freq_dist.variance(processFunc=lambda x:x[0]))
    logger.custom('date mean', web_date_dist.mean(processFunc=lambda x:x[0], isDate = True))
    logger.custom('date variance', web_date_dist.variance(processFunc=lambda x:x[0], isDate = True))
    freq_dist.showplot('Average Loaded Libraries Number on Each Web Rank', xlabel='# of loaded libs', ylabel='# webs', hist=True, processFunc=lambda x:x[0])


def mask(percent=0, reverse=False):
    # Mask high-star libraries (when reverse is False)
    res = conn2.selectAll('libs', ['library', 'starrank', 'star'])
    lib_blacklist = []
    lib_num = len(res)
    for entry in res:
        if entry[2] == 0:
            continue
        if not reverse and entry[1] <= lib_num * percent:
            lib_blacklist.append(entry[0])
        elif reverse and entry[1] >= lib_num * percent:
            lib_blacklist.append(entry[0])
    return lib_blacklist


if __name__ == '__main__':
    lib_blacklist = mask(0, reverse=False)
    analyze(DETECTION_RESULT_TABLE, lib_blacklist)
    logger.timecost()
    conn.close()
    conn2.close()