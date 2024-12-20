import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import json
import numpy as np
globalv = ultraimport('__dir__/../utils/globalv.py')

URL_BLACKLIST = ['partyrock.aws']
# WEBSITE_RANK_RANGE = (90 * 10000, 95 * 10000)
# SUFFIX = '1M'
# DETECTION_RESULT_TABLE = 'result_' + SUFFIX

def analyze(table_name, lib_blacklist, rank_range):
    res = conn.selectAll(table_name, ['rank', 'result', 'time', 'url'])
    avg_release_time_dist = Dist()
    freq_dist = Dist()
    web_date_dist = Dist()
    diversity_dist = Dist()

    release_num_dict = globalv.releaseNumInfo()

    i = 0
    # all_dates = []
    for entry in res:
        i += 1
        time = entry[2]
        if time < 0:
            # Error
            continue
        rank = int(entry[0])
        if rank < rank_range[0] * 10000 or rank > rank_range[1] * 10000:
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
                versions = lib['version']
                if libname in lib_blacklist or libname in globalv.FRAMEWORKS:
                    # Don't consider frameworks
                    in_blacklist += 1
                    continue
                diversity_dist.add(rank, libname)

                if 'date' not in lib:
                    continue
                date = lib['date']
                if date and len(date) >= 4:
                    
                    # Check whehter the library is fine-grained versioning
                    if not versions or len(versions) > 10:
                        continue
                    if len(versions) == 0:
                        if libname not in release_num_dict:
                            continue
                        elif release_num_dict[libname] > 10:
                            continue

                    # web_date_dist.add(rank, date)
                    
                    # all_dates.append(date)
                    dates.append(date)

            if len(dates) > 0:
                web_date_dist.add(rank, web_date_dist.avgDate(dates))
            freq_dist.add(rank, len(libs) - in_blacklist)
        # logger.leftTimeEstimator(len(res) - i)
    # avg_release_time_dist.showplot('Average Date of Libraries of Different Web Ranks', xlabel='rank', ylabel='avg. date', partition=20, processFunc=avg_release_time_dist.avgDate, dateY=True, yrange=['2010-01-01','2025-01-01'])
    # freq_dist.showplot('Average Loaded Libraries Number on Each Web Rank', xlabel='rank', ylabel='avg. # of loaded libs', partition=15, processFunc=lambda x:np.mean(x))
    # diversity_dist.showplot('Number of Different Libraries Used by Each Web Rank', xlabel='rank', ylabel='# libraries', partition=15, processFunc=lambda x:len(set(x)))
    # logger.custom('freq mean', freq_dist.mean(processFunc=lambda x:x[0]))
    # logger.custom('freq variance', freq_dist.variance(processFunc=lambda x:x[0]))
    # logger.custom('date mean', web_date_dist.mean(processFunc=lambda x:x[0], isDate = True))
    # logger.custom('date variance', web_date_dist.variance(processFunc=lambda x:x[0], isDate = True))

    freq_mean = freq_dist.mean(processFunc=lambda x:x[0])
    freq_variance = freq_dist.variance(processFunc=lambda x:x[0])
    date_mean = web_date_dist.mean(processFunc=lambda x:x[0], isDate = True)
    date_variance = web_date_dist.variance(processFunc=lambda x:x[0], isDate = True)
    # date_mean = web_date_dist.avgDate(all_dates)
    # date_variance = np.array(all_dates, dtype='datetime64[s]').view('i8').var()

    return round(float(freq_mean),2), round(float(freq_variance),2), date_mean, float(date_variance)

    # freq_dist.showplot('Average Loaded Libraries Number on Each Web Rank', xlabel='# of loaded libs', ylabel='# webs', hist=True, processFunc=lambda x:x[0])


def wrapper (lib_blacklist):
    web_tables = conn.show_tables()
    freq_mean_list = []
    freq_variance_list = []
    date_mean_list = []
    date_variance_list = []

    range_base = 0
    for table_name in globalv.WEB_DATASET:
        if table_name not in web_tables:
            continue
        logger.info(f'Analyzing the detection result table {table_name}...')
        r1, r2, r3, r4 = analyze(table_name, lib_blacklist, (range_base, range_base + 5))
        freq_mean_list.append(r1)
        freq_variance_list.append(r2)
        date_mean_list.append(r3)
        date_variance_list.append(r4)
        range_base += 5
        r1, r2, r3, r4 = analyze(table_name, lib_blacklist, (range_base, range_base + 5))
        freq_mean_list.append(r1)
        freq_variance_list.append(r2)
        date_mean_list.append(r3)
        date_variance_list.append(r4)
        range_base += 5
        

    logger.custom('freq mean', freq_mean_list)
    logger.custom('freq variance', freq_variance_list)
    logger.custom('date mean', date_mean_list)
    logger.custom('date variance', date_variance_list)


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
    wrapper(lib_blacklist)
    logger.timecost()
    conn.close()
    conn2.close()