'''
Created on 25 Apr 2020

@author: andreas
'''

import os, shutil
import pandas, wget

DATA_PATH = os.path.join("..", "data")
BNN_FILE = os.path.join(DATA_PATH, "GermanyKreisebene_Risklayer_bnn-20200425.csv")
TS_FILE =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer-20200425.csv")
TS_NEWEST =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer.csv")
PICS_PATH = os.path.join(DATA_PATH, "..", "pics")
PAGES_PATH = os.path.join(DATA_PATH, "..", "pages")

RISKLAYER_URL01 = "http://risklayer-explorer.com/media/data/events/GermanyValues.csv"
RISKLAYER_URL02 = "https://docs.google.com/spreadsheets/d/1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s/" 
RISKLAYER_URL02_SHEET = "bnn"

OPENDATASOFT_URL01 = "https://public.opendatasoft.com/explore/dataset/landkreise-in-germany/table/"
OPENDATASOFT_URL02 = "https://public.opendatasoft.com/explore/dataset/landkreise-in-germany/download/?format=csv&lang=en&use_labels_for_header=true&csv_separator=%3B"
OPENDATASOFT_PATH = os.path.join(DATA_PATH, "landkreise-in-germany.csv")
DISTANCES_PATH = os.path.join(DATA_PATH, "distances.csv")

def downloadData():
    print ("TODO daily")
    print (RISKLAYER_URL01)
    filename = wget.download(RISKLAYER_URL01, out=DATA_PATH)
    print ("downloaded:", filename)
    ts=pandas.read_csv(filename)
    last_col = ts.columns[2:].tolist()[-1]
    print ("newest column:", last_col)
    d=last_col.split(".")
    d.reverse()
    last_date = "".join(d)
    newfilename = TS_FILE.replace("20200425", last_date)
    print (newfilename)
    shutil.move(filename,newfilename)
    shutil.copy(newfilename, TS_NEWEST)
    
    # print ("TODO perhaps")
    # print (RISKLAYER_URL02)
    # print ("sheet", RISKLAYER_URL02_SHEET)
    
    
def repairData(ts, bnn):
    print ("repair dirty risklayer data:")
    print ("e.g. 12.03.20203 --> 12.03.2020")
    print ("TODO: ... e.g. 10000 --> 1000 in bnn!k2")
    newcols = ["12.03.2020" if x=="12.03.20203" else x for x in ts.columns]
    ts.columns = newcols
    # print (ts.columns)
    return ts, bnn 

    

def load_data(ts_f=TS_NEWEST, bnn_f=BNN_FILE):
    ts=pandas.read_csv(ts_f)
    bnn=pandas.read_csv(bnn_f)
    print ("\nLoading data from RiskLayer. This is their message:")
    print ("\n".join(ts[ts.ADMIN.isna()]["AGS"].tolist()))
    print()
    # now drop those info lines which are not data:
    ts.drop(ts[ts.ADMIN.isna()].index, inplace=True)
    ts, bnn = repairData(ts, bnn)
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

    # downloadData(); exit()
    # load_data(); exit()

    ts, bnn = data(withSynthetic=True)
    
    print()
    
    print (ts[ts["AGS"]=="00000"].drop(["AGS", "ADMIN"], axis=1).values.tolist())
    pass
