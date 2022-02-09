# -*- coding: utf-8 -*-
"""
@author: ASR1760
"""
import pandas as pd
import requests
import numpy as np
import timestring
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import sqlite3
from datetime import datetime
import os


root_url = 'http://ultrasignup.com'
race_path = '/entrants_event.aspx?did=87878'
directory = 'U://ultra_stuff//grand_slam//wser//dashboard//'
pd.set_option('display.max_rows', 90)
conn = sqlite3.connect(directory + 'ws-ca.db')
os.chdir(directory)

def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def get_race_entries(root_url, race_path, racename):
    res_url = root_url + race_path
    race_lst = requests.get(res_url, verify = False).text
    filename = directory + racename + '.csv'
    f = open(filename, 'w')
    f.write(race_lst)
    f.close()
    return race_lst

ws_ca = get_race_entries(root_url, race_path, 'ws-ca')
soup = BeautifulSoup(ws_ca, 'html.parser')

my_list = []
for att in soup.find_all('td'):
    my_list.append(att.get_text().strip())

my_list_formatted = []
temp_list = []
for x in range(len(my_list)):
    temp_list.append(my_list[x])
my_list_formatted.append(temp_list)

roster = list(divide_chunks(my_list_formatted[0], 14))

results_df = pd.DataFrame(roster, columns=['oa_rank','age_rank','ultra_count','target','age_group','trophy','first_name',
                            'last_name','city','state','bib','finishes','camera','results'])
results_df = results_df.astype(dtype= {'ultra_count':'int'})
results_df = results_df.drop(['results', 'target', 'bib', 'camera', 'trophy', 'finishes'], axis = 1)
results_df.sort_values(by = 'oa_rank', ascending = False)
results_df['oa_rank'] = results_df['oa_rank'].str.replace('%','')
results_df['age_rank'] = results_df['age_rank'].str.replace('%','')
results_df['create_date'] = datetime.now().date()
results_df = results_df.reset_index(drop = True)
results_df.to_csv('wser_stats.csv')
# conn.execute("DROP TABLE ws_ca_compare;")
# conn.execute("CREATE TABLE ws_ca_compare (oa_rank FLOAT, age_rank FLOAT, ultra_count INT, \
#               age_group VARCHAR(6), first_name VARCHAR(20), last_name VARCHAR(50), \
#               city VARCHAR(25), state CHAR(2), create_date DATE, PRIMARY KEY (first_name, last_name, city, state, create_date));")
# conn.execute("DELETE FROM ws_ca_compare WHERE create_date = DATE('NOW','LOCALTIME');")
# conn.commit()
results_df.to_sql('ws_ca_compare', con = conn, if_exists = 'append', index = False)
conn.commit()
cursor = conn.execute("""SELECT DISTINCT create_date
                            FROM ws_ca_compare
                            ORDER BY create_date DESC
                            LIMIT 2;""")

date1 = cursor.fetchone()[0]
date2 = cursor.fetchone()[0]

#deletes
cursor = conn.execute("""SELECT * FROM (SELECT * FROM ws_ca_compare
                                        WHERE create_date = '""" + str(date2) + """') y
                        LEFT JOIN (SELECT * FROM ws_ca_compare
                                        WHERE create_date = '""" + str(date1) + """') t
                        ON y.first_name = t.first_name
                        AND y.last_name = t.last_name
                        AND y.city = t.city
                        AND y.state = t.state
                        WHERE t.first_name IS NULL;""")

deletes = []
for row in cursor:
    deletes.append(row[0:9])

#adds
cursor = conn.execute("""SELECT * FROM (SELECT * FROM ws_ca_compare
                                        WHERE create_date = '""" + str(date1) + """') y
                        LEFT JOIN (SELECT * FROM ws_ca_compare
                                       WHERE create_date = '""" + str(date2) + """') t
                        ON y.first_name = t.first_name
                        AND y.last_name = t.last_name
                        AND y.city = t.city
                        AND y.state = t.state
                        WHERE t.first_name IS NULL;""")

adds = []
for row in cursor:
    adds.append(row[0:9])

# conn.execute("DROP TABLE ws_ca_drop_add;")
# conn.commit()
# conn.execute("CREATE TABLE ws_ca_drop_add (oa_rank FLOAT, age_rank FLOAT, ultra_count INT, \
#                age_group VARCHAR(6), first_name VARCHAR(20), last_name VARCHAR(50), \
#                city VARCHAR(25), state CHAR(2), modify_date DATE, add_drop VARCHAR(4), PRIMARY KEY (add_drop, first_name, last_name, city, state, modify_date));")
# conn.commit()

df_add = pd.DataFrame(adds, columns = ['oa_rank', 'age_rank', 'ultra_count', 'age_group',
                            'first_name','last_name', 'city', 'state', 'modify_date'])
df_add['add_drop'] = 'add'

df_drop = pd.DataFrame(deletes, columns = ['oa_rank', 'age_rank', 'ultra_count', 'age_group',
                            'first_name', 'last_name', 'city', 'state','modify_date'])
df_drop['add_drop'] = 'drop'

df_add.to_sql('ws_ca_drop_add', con = conn, if_exists = 'append', index = False)
df_drop.to_sql('ws_ca_drop_add', con = conn, if_exists = 'append', index = False)
conn.commit()

cursor = conn.execute("""SELECT COUNT(*) FROM ws_ca_compare 
                         WHERE create_date = '""" + str(date1) + """';""")
for row in cursor:
    print('2022 Western States 100 Miler Entrant Statistics')
    print('')
    print('Total number of entrants as of',str(date1) + ':', row[0])
    print('')

cursor = conn.execute("""SELECT AVG(oa_rank) FROM ws_ca_compare 
                         WHERE create_date = '""" + str(date1) + """' AND SUBSTR(age_group,1,1) = 'M';""")

m_rank = cursor.fetchone()[0]
print('Average male ranking:', round(m_rank,2))

cursor = conn.execute("""SELECT AVG(oa_rank) FROM ws_ca_compare 
                         WHERE create_date = '""" + str(date1) + """' AND SUBSTR(age_group,1,1) = 'F';""")

f_rank = cursor.fetchone()[0]
print('Average female ranking:', round(f_rank,2))

cursor = conn.execute("""SELECT AVG(ultra_count) FROM ws_ca_compare 
                         WHERE create_date = '""" + str(date1) + """' AND SUBSTR(age_group,1,1) = 'F';""")

ultra_count = cursor.fetchone()[0]
print('Average number of ultras:', round(ultra_count,2))
print('')

cursor = conn.execute("""SELECT * FROM ws_ca_drop_add
                         ORDER BY modify_date DESC;""")

print('All adds and deletes:')
for row in cursor:
    print(row)

conn.close()

##get waitlist
root_url = 'https://www.wser.org'
race_path = '/2022-wait-list'

ws_ca = get_race_entries(root_url, race_path, 'wait_list-ws')
soup = BeautifulSoup(ws_ca, 'html.parser')

my_list = []
for att in soup.find_all('td'):
    my_list.append(att.get_text().strip())

my_list_formatted = []
temp_list = []
for x in range(len(my_list)):
    temp_list.append(my_list[x])
my_list_formatted.append(temp_list)

roster = list(divide_chunks(my_list_formatted[0], 9))

results_df = pd.DataFrame(roster, columns=['position','mod_date','last_name','first_name','gender','city','state','country',
                                            'ticket_count'])
results_df = results_df.astype(dtype= {'ticket_count':'int'})
results_df['create_date'] = datetime.now().date()
results_df = results_df.reset_index(drop = True)
results_df.to_csv('wser_wait_list.csv')


np.random.choice(['Abel','Adam','Christina','John','Trevor'],5,replace = False)