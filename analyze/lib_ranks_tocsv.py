# Generate the library rankings based on detection results and save to csv files

import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Detection')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
Dist = ultraimport('__dir__/../utils/stat.py').Distribution
import json
import pandas as pd

URL_BLACKLIST = []
DETECTION_RESULT_TABLE = 'result_100k'
RANK_SAVE_PATH = 'data/LibRank/'

def starrank():
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])

    stardict = {}
    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue
        url = entry[2]
        if url in URL_BLACKLIST:
            continue
        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                libname = lib['libname']
                if libname not in stardict:
                    res2 = conn2.fetchone(f"SELECT `star` FROM `libs_cdnjs` WHERE `libname`='{libname}'")
                    if res2:
                        stardict[libname] = res2[0]
                    else:
                        stardict[libname] = 0
    
    stardict = dict(sorted(stardict.items(), key=lambda x:x[1], reverse=True))
    df = pd.DataFrame(columns=['rank', 'library', 'star'])
    for pair in stardict.items():
        new_row = {'rank': len(df)+1, 'library': pair[0], 'star': pair[1]}
        df = df._append(new_row, ignore_index=True)
    filepath = f'{RANK_SAVE_PATH}/byStar.rank.csv'
    df.to_csv(filepath, index=False)
    logger.info(f'Github star ranking is saved to the location: {filepath}')


def analyze():
    res = conn.selectAll(DETECTION_RESULT_TABLE, ['result', 'time', 'url', 'rank'])

    date_dict = Dist()
    freq_dict = Dist()
    for entry in res:
        time = entry[1]
        if time < 0:
            # Error
            continue
        url = entry[2]
        if url in URL_BLACKLIST:
            continue

        libs = json.loads(entry[0])
        if libs:
            for lib in libs:
                libname = lib['libname']
                freq_dict.add(libname)    
                if 'date' not in lib:
                    continue
                date = lib['date']       

                     

                if date and len(date) >= 4:
                    date_dict.add(libname, date)


    df = pd.DataFrame(columns=['rank', 'library', 'frequency'])
    for pair in freq_dict.freqDict().items():
        new_row = {'rank': len(df)+1, 'library': pair[0], 'frequency': pair[1]}
        df = df._append(new_row, ignore_index=True)
    filepath = f'{RANK_SAVE_PATH}/byFreq.rank.csv'
    df.to_csv(filepath, index=False)
    logger.info(f'Frequency ranking is saved to the location: {filepath}')

    df2 = pd.DataFrame(columns=['rank', 'library', 'avg. date'])
    for pair in date_dict.avgDateDict().items():
        new_row = {'rank': len(df2)+1, 'library': pair[0], 'avg. date': pair[1]}
        df2 = df2._append(new_row, ignore_index=True)
    filepath2 = f'{RANK_SAVE_PATH}/byDate.rank.csv'
    df2.to_csv(filepath2, index=False)
    logger.info(f'Average version date ranking is saved to the location: {filepath2}')

if __name__ == '__main__':
    analyze()
    starrank()
    conn.close()
    logger.close()