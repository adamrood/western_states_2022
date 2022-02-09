import pandas as pd
import numpy as np
import os
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
import datetime

os.chdir('u:\\ultra_stuff\\grand_slam\\wser\\operation_silver')

wser_df_2017 = pd.read_csv('.\\wser2017.csv')
wser_df_2018 = pd.read_csv('.\\wser2018.csv')
wser_df_2019 = pd.read_csv('.\\wser2019.csv')
wser_df_2021 = pd.read_csv('.\\wser2021.csv')

wser_df = pd.concat([wser_df_2017, wser_df_2018, wser_df_2019, wser_df_2021], ignore_index=True)

def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def get_time(seconds):
    return str(datetime.timedelta(seconds=seconds))

for x in wser_df.columns[:-2]:
    wser_df[x] = wser_df[x].str.replace('--:--','00:00:00')
    for y in range(len(wser_df)):
        if ((len(wser_df[x].iloc[y]) == 17) & (wser_df[x].iloc[y] != '00:00:00')):
            wser_df[x].iloc[y] = wser_df[x].iloc[y][0:8]
        if ((len(wser_df[x].iloc[y]) == 17) & (wser_df[x].iloc[y] == '00:00:00')):
            wser_df[x].iloc[y] = wser_df[x].iloc[y][:-8]
        if len(wser_df[x].iloc[y]) == 14:
            wser_df[x].iloc[y] = wser_df[x].iloc[y][6:]
        else:
            next
    wser_df[x] = wser_df[x].map(get_sec)

wser_df.to_csv('.\\check.csv')

pairs = [list(wser_df.columns[x:x + 2]) for x in range(len(wser_df.columns[:-1]) - 2)]

#estimate times
for pair in pairs:
    reg_df = wser_df[pair]
    if len(reg_df.loc[reg_df[pair[0]] == 0]) == 0:
        next
    else:
        to_score = reg_df.loc[reg_df[pair[0]] == 0]
        train = reg_df.loc[(reg_df[pair[0]] != 0) & (reg_df[pair[1]] != 0)]
        x = train.iloc[:,1]
        y = train[pair[0]]
        x_pred = to_score.iloc[:,1]
        reg = linear_model.LinearRegression()
        reg.fit(x.values.reshape(-1,1), y)
        reg.score(x.values.reshape(-1,1), y)
        #predict
        y_pred = reg.predict(x_pred.values.reshape(-1,1))
        preds_df = pd.DataFrame(y_pred,columns=[pair[0]], index=x_pred.index)
        preds_df[pair[0]] = round(preds_df[pair[0]],0).astype(int)
        wser_df.update(preds_df)

print(wser_df)

wser_df.to_csv('.\\check.csv')

scaler = StandardScaler()
LR_preds = pd.DataFrame()
for aid_station in list(wser_df.columns[0:18]):
    x = wser_df[[aid_station]]
    scaler.fit(x)
    x = scaler.transform(x)
    y = wser_df[['SILVER']]
    log_reg = linear_model.LogisticRegression()
    log_reg.fit(x, y)
    print(aid_station,'-',log_reg.score(x, y))
    y_pred = log_reg.predict(x)
    y_pred_probs = log_reg.predict_proba(x)
    LR_preds[aid_station + '_PROB'] = y_pred_probs[:,1]

wser_df_converted = pd.DataFrame()

for x in list(wser_df.columns[0:19]):
    wser_df_converted[x] = wser_df[x].map(get_time)
print(wser_df)
final_df = pd.concat([wser_df, wser_df_converted, LR_preds], axis = 1)
final_df.to_csv('.\\lr_probs.csv')