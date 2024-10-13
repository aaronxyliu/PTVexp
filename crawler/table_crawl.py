


# xpath: //div[contains(@class,'swReactTableCell') and @data-table-col='1']


from lxml import html
import sys
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()

from pathlib import Path
import pandas as pd




def convertHTML2csv(df, htmlStr):
 
    #url="https://pro.similarweb.com/#/digitalsuite/markets/webmarketanalysis/mapping/Adult/999/3m?webSource=Desktop"
    # resp= requests.get(url)
    # print(resp)
    # tree = html.fromstring(resp.content)
    # print(tree)

    tree = html.fromstring(htmlStr) 
    elements = tree.xpath('//div[contains(@class,"swReactTableCell") and @data-table-col="1"]')
    logger.info(f'{len(elements)} rows are found.')
    for element in elements:
        url = ''.join(element.itertext()) # Extract all the text inside this element
        new_row = {'rank': len(df)+1, 'url': url}
        df = df._append(new_row, ignore_index=True)
    
    return df


if __name__ == '__main__':
    # Usage: python3 crawler/table_crawl.py
    if len(sys.argv) == 0:
        logger.info('Need provide the output csv name.')
    
    file_path = Path(f'data/CategoryRank/{sys.argv[1]}.csv')

    # file = None
    df = None
    if not file_path.exists():
        df = pd.DataFrame(columns=['rank', 'url'])
    else:
        df = pd.read_csv(file_path)

    with open('crawler/data.html', 'r') as file:
        htmlStr = file.read()
    
    df = convertHTML2csv(df, htmlStr)
    df.to_csv(file_path, index=False)
    logger.info(f'Results saved to the file: {file_path}')

    