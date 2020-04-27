'''
Created on 25 Apr 2020

@author: andreas
'''

import os
import pandas

DATA_PATH = os.path.join("..", "data")
BNN_FILE = os.path.join(DATA_PATH, "GermanyKreisebene_Risklayer_bnn-20200425.csv")
TS_FILE =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer-20200425.csv")
PICS_PATH = os.path.join(DATA_PATH, "..", "pics")
PAGES_PATH = os.path.join(DATA_PATH, "..", "pages")

RISKLAYER_URL01 = "risklayer-explorer.com/media/data/events/GermanyValues.csv"
RISKLAYER_URL02 = "https://docs.google.com/spreadsheets/d/1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s/" 
RISKLAYER_URL02_SHEET = "bnn"

def downloadData():
    print ("TODO daily")
    print (RISKLAYER_URL01)
    
    print ("TODO perhaps")
    print (RISKLAYER_URL02)
    print ("sheet", RISKLAYER_URL02_SHEET)
    
    
def repairData():
    print ("TODO")
    print ("e.g. 12.03.20203 --> 12.03.2020")
    print ("e.g. 10000 --> 1000 in bnn!k2")
    

def load_data(ts_f=TS_FILE, bnn_f=BNN_FILE):
    ts=pandas.read_csv(ts_f)
    bnn=pandas.read_csv(bnn_f)
    return ts, bnn


def add_synthetic_data(ts, bnn, flatUntil = 14, steps=[10, 20, 50, 100, 130, 140, 150]):
    
    # infections: plus 20 plus 60 plus 20 then nothing new.
    
    synthetic_data = [0]*flatUntil  + steps + ([steps[-1]] * (len(ts.columns)-2-flatUntil-len(steps)))
    row = pandas.Series(["00000", "Dummykreis"]+synthetic_data, index=ts.columns)
    ts=ts.append(row, ignore_index=True)
    
    # some deterministic demography data, e.g. for unit testing 
    synthetic_landkreis = [0, "Dummykreis", "Landkreis", 150000, 100, 0.67,
                           0, 300,"Dummyland", 400000, 0.75]
    row = pandas.Series(synthetic_landkreis, index=bnn.columns)
    bnn=bnn.append(row, ignore_index=True)

    return ts, bnn


def data(withSynthetic=True):
    ts, bnn = load_data()
    if withSynthetic:
        ts, bnn = add_synthetic_data(ts, bnn)
    return ts, bnn


if __name__ == '__main__':

    ts, bnn = data(withSynthetic=True)
    
    print (ts[ts["AGS"]=="00000"].drop(["AGS", "ADMIN"], axis=1).values.tolist())
    pass
