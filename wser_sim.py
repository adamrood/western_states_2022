# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 10:22:53 2017
*********************
*                   *
* WSER SIMULATOR!!! *
*                   *
*********************
@author: ASR1760
"""

import pandas as pd
import time

start_time = time.time()

print('Western States Endurance Run Lottery Simulator')
print('by Adam S. Rood, Last updated:  05/21/18')

entrants = pd.DataFrame(columns=['years_in','count_runners','no_tickets'], index=[0])

#2017 ticket counts
entrants.loc[0] = [1,2658,1]
entrants.loc[1] = [2,1060,2]
entrants.loc[2] = [3,668,4]
entrants.loc[3] = [4,283,8]
entrants.loc[4] = [5,161,16]
entrants.loc[5] = [6,71,32]
entrants.loc[6] = [7,8,64]
entrants.loc[7] = [8,0,128]
entrants.loc[8] = [9,0,256]
entrants.loc[9] = [10,0,512]

max_year = 7
spots_available = 261
wait_list_size = 50
number_of_sims = int(input('How many simulations would you like to run?  '))
print ('Running ' + str(number_of_sims) + ' simulation(s)...')

i = 0
j = 0

tickets_summary = pd.DataFrame(columns=['runner_no','ticket_count','years_in'], index=[0])

ticket_count = entrants.iloc[j,2]
runner_no = 1

for years in range(max_year):
    for x in range(entrants.loc[j][1]):
        tickets_summary.loc[i] = [runner_no,ticket_count,entrants.iloc[j,0]]
        runner_no = runner_no + 1
        i = i + 1
    j = j + 1
    ticket_count = entrants.iloc[j,2]

tickets_master = pd.DataFrame(columns=['runner_no','ticket_no','years_in'], index=[0])

i = 0
j = 0 

for y in range(len(tickets_summary)):
    no_of_tix = tickets_summary.iloc[j][1]
    ticket_counter = 1
    for x in range(1,no_of_tix + 1):
        tickets_master.loc[i] = tickets_summary.iloc[j,0],ticket_counter,tickets_summary.iloc[j,2]
        ticket_counter = ticket_counter + 1
        i = i + 1
    j = j + 1
    
main_draw = pd.DataFrame(columns=['drawing_no','runner_no','ticket_no','years_in'], index=[0])
wait_list = pd.DataFrame(columns=['drawing_no','runner_no','ticket_no','years_in'], index=[0])

i = 0
j = 0
drawing_no = 1
tickets_live = tickets_master

while drawing_no <= number_of_sims:
    #main drawing loop
    for y in range(1,spots_available + 1):
        runner_pick = tickets_live.sample(n=1)
        main_draw.loc[i] = drawing_no,runner_pick.iloc[0,0],runner_pick.iloc[0,1],runner_pick.iloc[0,2]
        i = i + 1
        tickets_live = tickets_live[tickets_live.runner_no != runner_pick.iloc[0,0]]
    #waitlist
    for y in range(1,wait_list_size + 1):
        runner_pick = tickets_live.sample(n=1)
        wait_list.loc[j] = drawing_no,runner_pick.iloc[0,0],runner_pick.iloc[0,1],runner_pick.iloc[0,2]
        j = j + 1
        tickets_live = tickets_live[tickets_live.runner_no != runner_pick.iloc[0,0]]
        
    drawing_no = drawing_no + 1
    tickets_live = tickets_master

print(str(drawing_no - 1) + ' simulation(s) were completed in '
     + str(round((time.time() - start_time)/60, 2)) + ' minutes!')

#Output:  This needs cleaned up some.

#Main Drawing
summary_stats_main_draw = main_draw.groupby(['drawing_no','years_in'])['runner_no'].count().reset_index(name='total')

for y in range(1, number_of_sims + 1):
    for x in range(1,max_year + 1):
        summary_stats_main_draw.loc[len(summary_stats_main_draw)] = y, x, 0
                                    
summary_stats_main_draw_zeros = summary_stats_main_draw.groupby(['drawing_no','years_in'])['total'].max().reset_index(name = 'total')

main_draw_all = pd.merge(summary_stats_main_draw_zeros,entrants[['years_in','count_runners']], 
                      on='years_in', how='inner')

main_draw_all['probability'] = main_draw_all['total']/main_draw_all['count_runners']

final_stats_main_draw = main_draw_all.groupby('years_in').agg({'total':['min','max','mean'], 
                                   'probability':['min','max','mean']})

##Wait List Drawing
summary_stats_wait_list = wait_list.groupby(['drawing_no','years_in'])['runner_no'].count().reset_index(name='total')

for y in range(1, number_of_sims + 1):
    for x in range(1,max_year + 1):
        summary_stats_wait_list.loc[len(summary_stats_wait_list)] = y, x, 0
                                    
summary_stats_wait_list_zeros = summary_stats_wait_list.groupby(['drawing_no','years_in'])['total'].max().reset_index(name = 'total')
        
wait_list_all = pd.merge(summary_stats_wait_list_zeros,entrants[['years_in','count_runners']], 
                      on='years_in', how='inner')

wait_list_all['probability'] = wait_list_all['total']/wait_list_all['count_runners']

final_stats_wait_list = wait_list_all.groupby('years_in').agg({'total':['min','max','mean'], 
                                   'probability':['min','max','mean']})    

##Combined Drawings
combine = pd.merge(main_draw_all[['years_in','drawing_no','count_runners','total']],
                      wait_list_all[['years_in','drawing_no','count_runners','total']], 
                                   on=['years_in','drawing_no','count_runners'], how='inner')

combine['total'] = combine['total_x'] + combine['total_y']
combine['probability'] = combine['total']/combine['count_runners']

final_stats_all = combine.groupby('years_in').agg({'total':['min','max','mean'], 
                                   'probability':['min','max','mean']})   
    
print(final_stats_main_draw)
print(final_stats_wait_list)
print(final_stats_all)
