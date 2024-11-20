# Generate the library rankings based on detection results and save to the database

import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection3')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Statistics')
conn4 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import json
import numpy as np

URL_BLACKLIST = []
SUFFIX = '200k'
DETECTION_RESULT_TABLE = 'result_' + SUFFIX
RANK_SAVE_TABLE = 'libs_' + SUFFIX

FINE_GRAIN_THRESHOLD = 10   # The threshold of the number of releases to be considered as fine-grain versioning (<= 10)

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
        conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['# releases', 'release range', 'latest date'],\
                (num, f'{res[num-1][0]} ~ {res[0][0]} ({res[num-1][1]} ~ {res[0][1]})', res[0][1]), 'library', libname)

def releaseNumInfo():
    libs = conn4.show_tables()
    release_num_dict = {}
    for libname in libs:
        release_num_dict[libname] = conn4.entry_count(libname)
    return release_num_dict


def updateAll():
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])

    date_dist = Dist()
    lib_dist = Dist()
    web_cnt = 0

    distance_dist = Dist()

    fine_grain_dist = Dist()
    release_num_dict = releaseNumInfo()


    i = 0
    for entry in res:
        i += 1
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
                versions = lib['version']
                date = lib['date']

                if 'dist' in lib:
                    if 'estimated_dist' in lib and lib['estimated_dist'] == True:
                        pass
                    else:
                        # Only consider the distance when it is accurate
                        distance_dist.add(libname, lib['dist'])
                    
                
                lib_dist.add(libname)
                version_num = len(versions)
                if version_num == 0:
                    if libname in release_num_dict:
                        if release_num_dict[libname] and release_num_dict[libname] <= FINE_GRAIN_THRESHOLD:
                            fine_grain_dist.add(libname)
                else:
                    if version_num <= FINE_GRAIN_THRESHOLD:
                        fine_grain_dist.add(libname)

                if date and len(date) >= 4:
                    date_dist.add(libname, date)
        logger.leftTimeEstimator(len(res) - i)

    avgdate_dict = date_dist.avgDateDict()
    freq_dict = lib_dist.freqDict()
    star_dict = lib_dist.dict.copy()
    fine_grain_freq_dict = fine_grain_dist.freqDict()
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
        `latest date` date DEFAULT NULL,
        `latest detectable version` varchar(500) DEFAULT NULL,
        `avg. date` date DEFAULT NULL,
        `# loaded` int DEFAULT NULL,
        `% loaded` float DEFAULT NULL,
        `% fine-grain version` float DEFAULT NULL,
        `avg. distance` int DEFAULT NULL,
        `% distance` float DEFAULT NULL
        ''')

    rank = 1
    for libname, star in star_dict.items():
        avgdate = None
        if libname in avgdate_dict:
            avgdate = avgdate_dict[libname]

        avg_distance = -1
        perc_distance = -1
        if libname in distance_dist.dict and len(distance_dist.dict[libname]) > 0:
            avg_distance = np.mean(distance_dist.dict[libname])
            if libname in release_num_dict and release_num_dict[libname] > 0:
                release_num = release_num_dict[libname]
                perc_distance = round(avg_distance * 100 / release_num, 1)

        conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['star', 'starrank', 'avg. date', '# loaded', '%% loaded', 'avg. distance', '%% distance'],\
            (star, rank, avgdate, freq_dict[libname], round(freq_dict[libname] * 100 / web_cnt, 1), avg_distance, perc_distance), 'library', libname)

        if freq_dict[libname] > 0:
            fine_grain_num = 0
            if libname in fine_grain_freq_dict:
                fine_grain_num = fine_grain_freq_dict[libname]
            conn3.update_otherwise_insert(RANK_SAVE_TABLE, ['%% fine-grain version'],\
            (round(fine_grain_num * 100 / freq_dict[libname], 1),), 'library', libname)
        
        basicInfo(libname)
        dateInfo(libname)
        rank += 1
    logger.info(f'Results saved to the database table {RANK_SAVE_TABLE}.')
        

if __name__ == '__main__':
    updateAll()
    logger.timecost()
    conn.close()
    conn2.close()
    conn3.close()
    logger.close()