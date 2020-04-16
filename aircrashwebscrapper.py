import requests
import re
from bs4 import BeautifulSoup

url_base = 'http://www.planecrashinfo.com'
URL = '{}/database.htm'.format(url_base)
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

a_list = soup.find_all('a')

annual_link = []
for a_link in a_list:
    re_match = re.search('/\d{4}/\d{4}.htm',a_link['href'])
    if re_match:
        start_index, end_index = re_match.span()
        ref_url = a_link['href'][start_index:end_index]
        data_url = '{}{}'.format(url_base,ref_url)
        crash_year = ref_url[1:5]
        year_meta_data = {'crash_year':crash_year, 'data_url': data_url}
        annual_link.append(year_meta_data)

def process_row_data(data_row):
    '''
    Extract Data elements from HTML Row Data

    Accepts
    Beautiful Soup Element

    Returns
    List of data extracted from element

    '''
    row_cols = data_row.find_all('td')
    crash_date = row_cols[0].get_text()
    crash_detail_ref = row_cols[0].find_all('a')[0]['href']
    detail_url = '{}/{}/{}'.format(url_base,crash_year,crash_detail_ref)
    location = row_cols[1].get_text()
    craft_type = row_cols[2].get_text()
    fatalities = row_cols[3].get_text()
    
    #Process Additional Details
    detail_page = requests.get(detail_url)
    detail_soup = BeautifulSoup(detail_page.content, 'html.parser')
    detail_rows = detail_soup.find_all('tr')
    #Extract content and Assign to variables
    detail_rows_p = map(lambda x : x.find_all('td')[1].get_text(),detail_rows[1:])
    crash_date,crash_time ,crash_location,crash_op ,flight_no,flight_route,ac_type , reg_no ,cn_in ,aboard,fatalities ,ground ,summary = detail_rows_p
    row_data =( [crash_date,detail_url,location,craft_type,fatalities,crash_time,
                    crash_location,crash_op,flight_no,flight_route,ac_type,reg_no,cn_in,
                    aboard,fatalities,ground,summary]
                )
    return row_data

crash_data = []
for year_link in annual_link[0:1]:
    crash_year = year_link['crash_year']
    print('==== Processing {} ===='.format(crash_year))
    year_url = year_link['data_url']
    year_page = requests.get(year_url)
    year_soup = BeautifulSoup(year_page.content, 'html.parser')
    
    grey_rows = year_soup.find_all('tr',bgcolor='DCDCDC')
    white_rows = year_soup.find_all('tr',bgcolor='WHITE')
    
    data_rows = grey_rows+white_rows
    
    for i,data_row in enumerate(data_rows):
        print('    == Row {} of {} =='.format(i+1,len(data_rows)))
        row_data = process_row_data(data_row)        
        row_data.append(crash_year)
        crash_data.append(row_data)

import pickle
with open('crash_data.data','wb') as cd:
    pickle.dump(crash_data,cd)
