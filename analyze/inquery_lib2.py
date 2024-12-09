import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
globalv = ultraimport('__dir__/../utils/globalv.py')

import sys
import json
import math

URL_BLACKLIST = []
MIN_SHOW_THRESHOLD = 100

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

    rank_dist = Dist()
    year_dist = Dist()
    version_len_dist = Dist()
    other_lib_dist = Dist()
    date_list = []
    web_cnt = 0
    lib_cnt = 0
    no_date_cnt = 0
    url_list = []

    web_tables = conn.show_tables()
    for table_name in globalv.WEB_DATASET:
        if table_name not in web_tables:
            continue
        logger.info(f'Analyzing the detection result table {table_name}...')
        res = conn.selectAll(table_name, ['result', 'time', 'url', 'rank'])

        accurate_version_dist = Dist()   # Accurate versioning (version range length = 1)
        fine_version_dist = Dist()  # Fine-grained versioning (version range length <= 10)
        all_version_dist = Dist()   # All versioning

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
            # if rank > 44900:
            #     print(rank)
            if libs:
                for lib in libs:
                    if lib['libname'] != libname:
                        continue

    
                    

                    # url_list.append(url)

                    versions = lib['version']
                    if len(libs) > 300:
                        # Detection error
                        continue

                    for otherlib in libs:
                        if otherlib['libname'] != libname:
                            other_lib_dist.add(otherlib['libname'])
                    version_len_dist.add(len(versions))
                    date = lib['date']

                    url_list.append(url)
                    
                    lib_cnt += 1
                    if len(versions) == 0:
                        

                        pass
                    else:
                        if len(versions) == 1:
                            accurate_version_dist.add(str(versions[0]))
                            all_version_dist.add(str(versions[0]))
                        if len(versions) <= 10:
                            fine_version_dist.add(str(versions[int(len(versions)/2)]))
                        if len(versions) > 1:
                            all_version_dist.add(f"{str(versions[0])}~{str(versions[-1])}")


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

    logger.info(other_lib_dist.freqDict(f'Other Libraries Companied with {libname}'))
    # year_dist.showplot(f'Version Year Distribution of {libname}', xlabel='year', ylabel='# occurrences', sortByX=True)
    all_version_dist.showplot(f'Version Distribution of {libname}', xlabel='version', verX=True, ylabel='# occurrences', sortByX=True, thresY=MIN_SHOW_THRESHOLD)
    # version_len_dist.showplot(f'Version Range Length Distribution of {libname}', xlabel='length', ylabel='# occurrences', sortByX=True)

    # rank_dist.showplot(f'Frequency of {libname} on Different Ranks of Websites', xlabel='website rank', ylabel='# occurrences')
    # logger.info(rank_dist.avgDateDict(f'Average Release Date of {libname} on Different Ranks of Websites'))

    logger.outdent()
    logger.newline()

if __name__ == '__main__':
    # Usage: python3 analyze/inquery_lib2.py jquery
    if len(sys.argv) == 1:
        logger.info('Need provide the library name.')
    elif len(sys.argv) == 2:
        libname = sys.argv[1]
        basicInfo(libname)
        dateInfo(libname)
        analyze(libname)
    conn.close()
    logger.close()