'''
Created on 26 Apr 2020

@author: andreas
'''

import os, copy
import datetime as dt

import pandas

import dataFiles



def find_AGS(ts, name):
    cond = ts['ADMIN'].str.contains(name, na=False)
    # return cond
    rows = ts.loc[cond]
    return rows

def to_dt(dt_str):
    d = list(map(int, dt_str.split(".")))
    # print(d)
    return dt.datetime(d[2], d[1], d[0])

def dates_list(ts):
    """
    extract the table headings = dates, in German formatting. 
    """
    dates=[to_dt(d) for d in ts.columns[2:].values]
    # print (dates)
    # ts.values[0]
    return dates

def AGS_to_ts_total(ts, AGS):
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    return row.values[0][2:].tolist()


def AGS_to_ts_daily(ts, AGS):
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    row = row.drop(['AGS', 'ADMIN'], axis=1)
    # return row
    diff = row.diff(axis=1)
    return diff.values[0].tolist()
    

def AGS_to_population(bnn, AGS):
    # AGS = ("00000"+AGS)[-5:]
    AGS = int(AGS)
    # print(AGS)
    row = bnn.loc[bnn['AGS'] == AGS]
    pop = row["Population"].values[0] 
    inf = row["Infections"].values[0] 
    gen = row["GEN"].values[0] 
    bez = row["BEZ"].values[0] 
    return gen, bez, inf, pop


def AGS_to_Bundesland(bnn, AGS):
    # AGS = ("00000"+AGS)[-5:]
    AGS = int(AGS)
    row = bnn.loc[bnn['AGS'] == AGS]
    name = row["Bundesland"].values[0] 
    inf_BL = row["Infections_Bundesland"].values[0] 
    pop_BL = row["Population_Bundesland"].values[0] 
    return name, inf_BL, pop_BL


def temporal_center(data):
    """
    find 'center' index of data by 
    multiplying height with index, and dividing by sum of heights
    
    TODO: what to do with the negative values?
          Cut them out before summing perhaps?
          On the other hand, they (temporarily-)LOCALLY correct over-reported cases, right?
          So perhaps better to leave them in?
    """
    ddata = data[1:] # drop the nan in the first cell, i.e. shift left
    productsum = sum([d*(i+1) for i,d in enumerate(ddata)]) # add one i.e. shift right
    center = productsum/sum(ddata) # + 1 - 1 # shift left and right equalize each other
    # synthetic "data" with one peak near center:
    signal = [0]*len(data)
    signal[int(round(center))]=max(ddata)*0.25
    return center, signal
    
    
def get_Kreis(ts, bnn, AGS):
    # get data and names
    gen, bez, inf, pop = AGS_to_population(bnn, AGS)
    name_BL, inf_BL, pop_BL = AGS_to_Bundesland(bnn, AGS)
    title = "%s (%s #%s, %s) Population=%d" % (gen, bez, AGS, name_BL, pop)
    filename = "Kreis_" + ("00000"+AGS)[-5:] + ".png"
    daily = AGS_to_ts_daily(ts, AGS)
    cumulative = AGS_to_ts_total(ts, AGS)
    return daily, cumulative, title, filename
   

def join_tables_for_and_aggregate_Bundeslaender(ts, bnn):

    # careful, there might be more fields with nan (currently just the 3 copyright rows)
    ts_int = copy.deepcopy(ts.dropna()) 
    
    ts_int["AGS"]=pandas.to_numeric(ts_int["AGS"]) # must transform string to int, for merge:
    ts_BuLa=pandas.merge(ts_int, bnn[["AGS", "Bundesland", "Population"]], how="left", on=["AGS"])

    Bundeslaender=ts_BuLa.drop(["AGS"], axis=1).groupby(["Bundesland"]).sum()
    print("consistency check, does this look like Germany's population? ", Bundeslaender["Population"].sum())

    return ts_BuLa, Bundeslaender


def get_BuLa(Bundeslaender, name):
    # get data and names
    filename = "bundesland_" + name + ".png"
    population = Bundeslaender.loc[name, "Population"]
    # row = Bundeslaender.loc[Bundeslaender['Bundesland'] == name]
    row = Bundeslaender.drop(["Population"], axis=1).loc[[name]]
    
    cumulative=row.values[0].tolist()
    diff = row.diff(axis=1)
    daily = diff.values[0].tolist()
    
    title = name + " Population=%d" % population
    
    return daily, cumulative, title, filename, population


if __name__ == '__main__':
    ts, bnn = dataFiles.data(withSynthetic=True)
    
    print (find_AGS(ts, "Osnabrück"))
    print (find_AGS(ts, "Heinsberg"))

    dates = dates_list(ts)

    AGS = "0"
    AGS = "1001"
    AGS = "5370"
    AGS = "9377"
    print(AGS_to_ts_total(ts, AGS))
    print(AGS_to_ts_daily(ts, AGS))
    
    gen, bez, inf, pop = AGS_to_population(bnn, AGS)
    print (gen, bez, inf, pop)
    name, inf_BL, pop_BL = AGS_to_Bundesland(bnn, AGS)
    print (name, inf_BL, pop_BL )
    
    data = AGS_to_ts_daily(ts, "0")
    print (len(data))
    data = AGS_to_ts_daily(ts, "00000")
    print (len(data))
    center, signal = temporal_center(data)
    print ("center at day %.2f" % center)
    
    print ("\nKreis")
    daily, cumulative, title, filename = get_Kreis(ts, bnn, AGS)
    print (daily, cumulative)
    print (title, filename)
    
    print ("\nBundesländer")
    ts_BuLa, Bundeslaender = join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    
    daily, cumulative, title, filename, population = get_BuLa(Bundeslaender, "Hessen")
    print (daily, cumulative)
    print (title, filename, population)
    