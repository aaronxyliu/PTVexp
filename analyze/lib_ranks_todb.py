# Generate the library rankings based on detection results and save to the database

import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
conn4 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import json

URL_BLACKLIST = []
SUFFIX = '1M'
DETECTION_RESULT_TABLE = 'result_' + SUFFIX
RANK_SAVE_TABLE = 'libs_' + SUFFIX


def basicInfo(libname):
    res = conn2.fetchone(f"SELECT `latest version`, `cdnjs`, `url` FROM `libs_cdnjs` WHERE `libname`='{libname}'")
    if res:
        conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['latest detectable version', 'cdnjs', 'url'],\
                                  (res[0], res[1], res[2]), 'library', libname)

def dateInfo(libname):
    try:
        res = conn4.fetchall(f"SELECT `tag_name`, `publish_date` FROM `{libname}` ORDER BY `publish_date` DESC")
    except:
        return
    if res:
        num = len(res)
        conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['# releases', 'release range'],\
                (num, f'{res[num-1][0]} ~ {res[0][0]} ({res[num-1][1]} ~ {res[0][1]})'), 'library', libname)


def updateAll():
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])

    date_dist = Dist()
    lib_dist = Dist()
    web_cnt = 0

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
                date = lib['date']
                lib_dist.add(libname)

                if date and len(date) >= 4:
                    date_dist.add(libname, date)

    avgdate_dict = date_dist.avgDateDict()
    freq_dict = lib_dist.freqDict()
    star_dict = lib_dist.dict.copy()
    for libname in star_dict:
        res2 = conn2.fetchone(f"SELECT `star` FROM `libs_cdnjs` WHERE `libname`='{libname}'")
        if res2:
            star_dict[libname] = res2[0]
        else:
            star_dict[libname] = 0
    
    # Sort based on Github star from high to low
    star_dict = dict(sorted(star_dict.items(), key=lambda x:x[1], reverse=True))

    conn3.create_new_table(RANK_SAVE_TABLE, '''
        `library` varchar(100) DEFAULT NULL,
        `star` int DEFAULT NULL,
        `starrank` int DEFAULT NULL,
        `cdnjs` varchar(500) DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        `# releases` int DEFAULT NULL,
        `release range` varchar(500) DEFAULT NULL,
        `latest detectable version` varchar(500) DEFAULT NULL,
        `avg. date` date DEFAULT NULL,
        `# loaded` int DEFAULT NULL,
        `% loaded` float DEFAULT NULL
        ''')

    rank = 1
    for libname, star in star_dict.items():
        avgdate = None
        if libname in avgdate_dict:
            avgdate = avgdate_dict[libname]

        conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['star', 'starrank', 'avg. date', '# loaded', '%% loaded'],\
            (star, rank, avgdate, freq_dict[libname], round(freq_dict[libname] * 100 / web_cnt, 1)), 'library', libname)
        
        basicInfo(libname)
        dateInfo(libname)
        rank += 1
    logger.info(f'Results saved to the database table {RANK_SAVE_TABLE}.')
        

if __name__ == '__main__':
    updateAll()
    conn.close()
    conn2.close()
    conn3.close()
    logger.close()