import pandas as pd
import sqlite3 as sql

def reformat(file,delimiter, con):
    regenie = pd.read_csv(file,delimiter)
    regenie = regenie.sort_values(by=['Chr','Pos'])
    regenie = regenie.reset_index().drop(columns = ['index'])
    for i in range(len(regenie)):
        r = len(regenie['Ref'][i])
        a = len(regenie['Alt'][i])
        if r>a:
            regenie.at[i,'Ref'] = regenie['Ref'][i][a:]
            regenie.at[i,'Alt'] = "-"
            regenie.at[i,'Pos'] += 1
        elif a>r:
            regenie.at[i,'Alt'] = regenie['Alt'][i][r:]
            regenie.at[i,'Ref'] = "-"
            regenie.at[i,'Pos'] += 1      
    c = sql.connect(con)
    regenie.to_sql("regenie",c,if_exists='replace')
    return None





