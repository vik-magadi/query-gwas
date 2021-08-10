#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import sqlite3 as sql

def reformat(file,delimiter):
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
    return regenie

con = sql.connect("var_m30_4oc.txt.sqlite")

r = reformat("trait_var_m30.csv","\t")

r.to_sql("regenie",con)