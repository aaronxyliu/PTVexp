# Crawl all libraries and their Github star number from Cdnjs
# Remember to set the CRAWER_LIMIT and the Github token

from urllib.request import Request, urlopen
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases_All')
conn3 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Tags')

OUTPUT_TABLE = 'libs_cdnjs_all_12_5'

def update_tag_info(libname, first_tag_tuple, last_tag_tuple):
    conn.update(OUTPUT_TABLE, ['first tag name', 'first tag date', 'last tag name', 'last tag date'],\
                (first_tag_tuple[0], first_tag_tuple[1], last_tag_tuple[0], last_tag_tuple[1]), f"`libname`='{libname}'")

def match_tag():
    release_table_names = conn2.show_tables()
    tag_table_names = conn3.show_tables()

    res = conn.selectAll(OUTPUT_TABLE, ['libname', 'github', 'cdnjs rank'])
    for entry in res:
        libname = entry[0]
        rank = entry[2]
        github_direct = entry[1][11:]

        # if rank < 1612:
        #     continue
        # elif rank > 1612:
        #     break

        tag_table_name = None
        if github_direct in tag_table_names:
            tag_table_name = github_direct
        elif github_direct[:50] in tag_table_names:
            tag_table_name = github_direct[:50]
        elif github_direct[:20] in tag_table_names:
            tag_table_name = github_direct[:20]
        if tag_table_name:
            first_tag_res = conn3.selectAll(tag_table_name, ['tag_name', 'publish_date'], limit=1, sortBy='publish_date', descending=False)
            last_tag_res = conn3.selectAll(tag_table_name, ['tag_name', 'publish_date'], limit=1, sortBy='publish_date', descending=True)
            update_tag_info(libname, first_tag_res[0], last_tag_res[0])

            continue
        

        release_table_name = None
        if github_direct in release_table_names:
            release_table_name = github_direct
        elif github_direct[:50] in release_table_names:
            release_table_name = github_direct[:50]
        elif github_direct[:20] in release_table_names:
            release_table_name = github_direct[:20]
        if release_table_name:
            first_tag_res = conn2.selectAll(release_table_name, ['tag_name', 'publish_date'], limit=1, sortBy='publish_date', descending=False)
            last_tag_res = conn2.selectAll(release_table_name, ['tag_name', 'publish_date'], limit=1, sortBy='publish_date', descending=True)
            update_tag_info(libname, first_tag_res[0], last_tag_res[0])

        






    
if __name__ == '__main__':
    match_tag()


    conn.close()
    logger.close()
