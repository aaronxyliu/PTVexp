import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution

import sys
import json
import math

URL_BLACKLIST = []
DETECTION_RESULT_TABLE = 'result_300k'

def basicInfo(libname):
    logger.info('=== BASIC INFORMATION ===')
    logger.indent()
    res = conn2.fetchone(f"SELECT `star`, `latest version`, `cdnjs` FROM `libs_cdnjs` WHERE `libname`='{libname}'")
    if res:
        logger.info(f'Gihub Star: {res[0]}')
        logger.info(f'Latest Detectable Version: {res[1]}')
        logger.info(f'Cdnjs URL: {res[2]}')
    logger.outdent()
    logger.newline()

def dateInfo(libname):
    logger.info('=== VERSION RELEASE DATE INFORMATION ===')
    try:
        res = conn3.fetchall(f"SELECT `tag_name`, `publish_date` FROM `{libname}`  ORDER BY `publish_date` DESC")
    except:
        logger.warning(f'No release date database is found.')
        logger.newline()
        return
    logger.indent()
    num = len(res)
    logger.info(f'# Releases: {num}')
    logger.info(f'Release Range: {res[num-1][0]} ~ {res[0][0]} ({res[num-1][1]} ~ {res[0][1]})')
    logger.outdent()
    logger.newline()

def analyze(libname):
    logger.info('=== DISTRIBUTION ANALYSIS ===')
    logger.indent()
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])

    rank_dist = Dist()
    year_dist = Dist()
    version_len_dist = Dist()
    date_list = []
    web_cnt = 0
    lib_cnt = 0
    no_date_cnt = 0
    url_list = []

    accurate_version_dist = Dist()   # Accurate versioning (version range length = 1)
    fine_version_dist = Dist()  # Fine-grained versioning (version range length <= 10)

    for entry in res:
        time = entry[1]
        url = entry[2]
        rank = entry[3]
        if time < 0:
            # Error
            continue
        if url in URL_BLACKLIST:
            continue
        web_cnt += 1
        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                if lib['libname'] != libname:
                    continue

                url_list.append(url)

                versions = lib['version']
                version_len_dist.add(len(versions))
                date = lib['date']
                
                lib_cnt += 1
                if len(versions) == 0:
                    pass
                else:
                    if len(versions) == 1:
                        accurate_version_dist.add(versions[0])
                    if len(versions) <= 10:
                        fine_version_dist.add(versions[int(len(versions)/2)])

                if date and len(date) >= 4:
                    date_list.append(date)
                    rank_dist.add(rank, date)
                    year = date[:4]
                    year_dist.add(year)
                else:
                    no_date_cnt += 1
                break
    

    
    logger.info(f'# total websites: {web_cnt}')
    logger.info(f'# websites containing {libname}: {lib_cnt} ({round(lib_cnt * 100 / web_cnt, 1)}%)')
    logger.info(url_list[:20])
    logger.info(f'# no date: {no_date_cnt}')
    if lib_cnt > 0:
        accu_num = accurate_version_dist.size()
        logger.info(f'# accurate versioning: {accu_num} ({round(accu_num * 100 / lib_cnt, 1)}%)')
        fine_num = fine_version_dist.size()
        logger.info(f'# fine-grained versioning: {fine_num} ({round(fine_num * 100 / lib_cnt, 1)}%)')
        logger.info(f'avg. release date in websites: {rank_dist.avgDate(date_list)}')
    # year_dist.showplot(f'Version Year Distribution of {libname}', xlabel='year', ylabel='# occurrences', sortByX=True)
    accurate_version_dist.showplot(f'Accurate Version Distribution of {libname}', xlabel='version', verX=True, ylabel='# occurrences', sortByX=True, thresY=50)
    # version_len_dist.showplot(f'Version Range Length Distribution of {libname}', xlabel='length', ylabel='# occurrences', sortByX=True)

    # rank_dist.showplot(f'Frequency of {libname} on Different Ranks of Websites', xlabel='website rank', ylabel='# occurrences')
    # logger.info(rank_dist.avgDateDict(f'Average Release Date of {libname} on Different Ranks of Websites'))

    logger.outdent()
    logger.newline()

if __name__ == '__main__':
    # Usage: python3 analyze/inquery_lib.py jquery
    if len(sys.argv) == 1:
        logger.info('Need provide the library name.')
    elif len(sys.argv) == 2:
        libname = sys.argv[1]
        basicInfo(libname)
        dateInfo(libname)
        analyze(libname)
    conn.close()
    logger.close()