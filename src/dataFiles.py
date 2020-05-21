'''
Created on 25 Apr 2020

@author: andreas
'''

import os, shutil
import pandas, wget, requests 
import bs4 as bs
import pandas as pd

REPO_PATH = ".."
DATA_PATH = os.path.join(REPO_PATH, "data")
BNN_FILE = os.path.join(DATA_PATH, "GermanyKreisebene_Risklayer_bnn-20200425.csv")
HAUPT_FILES = os.path.join(DATA_PATH, "GermanyKreisebene_Risklayer_haupt%s.csv")
WP_FILE =  os.path.join(DATA_PATH, "wikipedia_kreise_most.csv")
WP_URL="https://de.wikipedia.org/"

TS_FILE =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer-20200425.csv")
TS_NEWEST =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer.csv")
PICS_PATH = os.path.join(DATA_PATH, "..", "pics")
PAGES_PATH = os.path.join(DATA_PATH, "..", "pages")

WWW_REPO_PATH = os.path.join(DATA_PATH, "..", "..", "cov19de")
WWW_REPO_PICS = os.path.join(WWW_REPO_PATH, "pics")
WWW_REPO_PAGES = os.path.join(WWW_REPO_PATH, "pages")
WWW_REPO_PATH_GIT_SCRIPT = "./git-add-commit-push.sh"

ALSO_TO_BE_COPIED = ["index.html", "history.txt", "todo.md", "log.txt"]

RISKLAYER_URL01 = "http://risklayer-explorer.com/media/data/events/GermanyValues.csv"
# RISKLAYER_URL02 = "https://docs.google.com/spreadsheets/d/1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s/"
# RISKLAYER_URL02_SHEET = "bnn"

# naming 'Haupt' (in case they reorder their sheets, then gid=0 would point to the wrong one!)
# for syntax see https://stackoverflow.com/a/33727897
#     and https://developers.google.com/chart/interactive/docs/spreadsheets#query-source-ranges
# 
# https://docs.google.com/spreadsheets/d/1EZNqMVK6hCccMw4pq-4T30ADJoayulgx9f98Vui7Jmc/gviz/tq?tqx=out:csv&range=A5:AU406&sheet=Haupt
GOOGLEDOCS_ToCSV_WithSheetname="https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&range=%s&sheet=%s"
RISKLAYER_MASTER_SHEET_20200521 = "1EZNqMVK6hCccMw4pq-4T30ADJoayulgx9f98Vui7Jmc" # last night snapshot
RISKLAYER_MASTER_SHEET = "1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s" # Risklayer master
RISKLAYER_MASTER_SHEET_TABLE = ("Haupt", "A5:AU406")

# distances between districts:
OPENDATASOFT_URL01 = "https://public.opendatasoft.com/explore/dataset/landkreise-in-germany/table/"
OPENDATASOFT_URL02 = "https://public.opendatasoft.com/explore/dataset/landkreise-in-germany/download/?format=csv&lang=en&use_labels_for_header=true&csv_separator=%3B"
OPENDATASOFT_PATH = os.path.join(DATA_PATH, "landkreise-in-germany.csv")
DISTANCES_PATH = os.path.join(DATA_PATH, "distances.csv")


def repairData(ts, bnn):
    print ("\nRepair dirty risklayer data:")
    newcols = ["12.03.2020" if x=="12.03.20203" else x for x in ts.columns]
    if newcols!=ts.columns.tolist():
        print ("found and fixed 12.03.20203 --> 12.03.2020 (problem on 25/4/2020)")
    
    newcols2 = ["AGS" if x=='ï»¿AGS' else x for x in newcols]
    if newcols2!=newcols:
        print ("found and fixed ï»¿AGS --> AGS  (problem on 29/4/2020)")
        
    ts.columns = newcols2

    before = ts[ts["AGS"]=="05370"]["27.04.2020"]
    after  = ts[ts["AGS"]=="05370"]["28.04.2020"]
    # print (float(after) / float(before) ) 
    if float(after) / float(before) < 0.5:
        print ("huge drop of some values for 28.4.2020, e.g. Heinsberg: 1733.0  -->   1.739  -->  1743.0 (was a problem on 29/4/2020)")
        print ("temporary fix: interpolate 28. from 27. and 29.")
        ts["28.04.2020"]=(ts["29.04.2020"]+ts["27.04.2020"])/2

    # print ("Still unfixed: 10000 --> 1000 in bnn!k2 (i.e. fixed manually)") # solved in source table
    print()
    return ts, bnn


def inspectNewestData(ts):
    ts, _ = repairData(ts, [])
    
    # print (ts.columns)
    last3columns=ts.columns[-3:].tolist() + ["ADMIN"]
    df = ts[last3columns]
    print ("\nJust visual inspection - unless the following tables get VERY LONG - all is probably good ...\n(TODO: Automate this with two thresholds (number of, amount of drop)?)")
    print ("\nvalues going down for previous:")
    print (df[df[last3columns[1]]<df[last3columns[0]]])
    print ("\nvalues going down for newest:")
    print (df[df[last3columns[2]]<df[last3columns[1]]])
    
    print()
    print ("Totals:")
    datecolumns=ts.columns[-4:].tolist()
    df = ts[datecolumns].sum()
    # df["diff"]=df.diff()
    print (df.astype(int).to_string())
    print ("Diffs:")
    print (df.diff().dropna().astype(int, errors='ignore').to_string())
    # print (df)
    

def downloadData(andStore=True):

    print (RISKLAYER_URL01)
    filename = wget.download(RISKLAYER_URL01, out=DATA_PATH)
    print ("downloaded:", filename)

    ts=pandas.read_csv(filename, encoding='cp1252') # encoding='utf-8')
    last_col = ts.columns[2:].tolist()[-1]
    print ("newest column:", last_col)
    if andStore:
        d=last_col.split(".")
        d.reverse()
        last_date = "".join(d)
        newfilename = TS_FILE.replace("20200425", last_date)
        shutil.move(filename,newfilename)
        print (newfilename)
        shutil.copy(newfilename, TS_NEWEST)
        print (TS_NEWEST)
    else:
        warn = ("*" * 57 + "\n")*3
        print("\n" + warn + "ALERT: dev mode ... NOT storing this data\n"+ warn)
    
    inspectNewestData(ts)
    # print ("TODO perhaps")
    # print (RISKLAYER_URL02)
    # print ("sheet", RISKLAYER_URL02_SHEET)


def get_wikipedia_landkreise_table(url='https://de.wikipedia.org/wiki/Liste_der_Landkreise_in_Deutschland', 
                                   filename=WP_FILE):
    
    """
    todo: the same for https://de.wikipedia.org/wiki/Liste_der_kreisfreien_St%C3%A4dte_in_Deutschland
    """

    columns=['AGS', 'Kreis', 'Kreis_WP', 'KreisSitz', 'KreisSitz_WP', 'Einwohner', 'Fläche', 'Karte']
    df = pd.DataFrame(columns=columns)

    f = requests.get(url).text
    soup = bs.BeautifulSoup(f, 'lxml')
    parsed_table = soup.find_all('table')[0]


    for row in parsed_table.find_all('tr'):
        cells = list(row.find_all('td'))
        if cells:
            AGS=list(cells[0].stripped_strings)[0]

            lk=(list(cells[1].stripped_strings))[0]
            lk_wp = cells[1].a['href']

            lk_hs= (list(cells[4].stripped_strings))[0]
            lk_hs_wp = cells[4].a['href']

            lk_ew = int((list(cells[5].stripped_strings))[0].replace(".", ""))

            lk_fl_de = (list(cells[6].stripped_strings))[0]
            lk_fl = float(lk_fl_de.replace(".", "").replace(".", "").replace(",", "."))

            lk_pic = cells[8].img['src']
            
            datarow = [AGS, lk, lk_wp, lk_hs, lk_hs_wp, lk_ew, lk_fl, lk_pic]
            df=df.append(pd.DataFrame([datarow], columns=columns)) 
            
    df.to_csv(filename, index=False)
    return df

def load_wikipedia_landkreise_table(filepath=WP_FILE):
    df = pd.read_csv(filepath, index_col="AGS")
    return df


def load_data(ts_f=TS_NEWEST, bnn_f=BNN_FILE):
    ts=pandas.read_csv(ts_f, encoding='cp1252') # encoding='utf-8')
    bnn=pandas.read_csv(bnn_f)
    ts, bnn = repairData(ts, bnn)
    print ("\nLoading data from RiskLayer. This is their message:")
    print ("\n".join(ts[ts.ADMIN.isna()]["AGS"].tolist()))
    print()
    # now drop those info lines which are not data:
    ts.drop(ts[ts.ADMIN.isna()].index, inplace=True)
    # ts, bnn = repairData(ts, bnn)
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


def download_sheet_table(sheetID=RISKLAYER_MASTER_SHEET, table=RISKLAYER_MASTER_SHEET_TABLE, reindex="AGS"):
    risklayer_sheet_url = GOOGLEDOCS_ToCSV_WithSheetname % (sheetID, table[1], table[0])
    print ("Downloading this data:")
    print (risklayer_sheet_url)
    df=pandas.read_csv(risklayer_sheet_url) # error_bad_lines=False)
    if reindex:
        df.index=df[reindex].tolist() # index == AGS, easier access
    #print(df.columns.tolist())
    return df
    
def save_csv_twice(df, filestump=HAUPT_FILES):
    lastEntry=pandas.to_datetime(df.Zeit).max()
    print ("Last entry was:", lastEntry)
    timestamp=lastEntry.strftime("%Y%m%d_%H%M%S")
    filename1=filestump % ("-" + timestamp)
    df.to_csv(filename1, index=False)
    print(filename1)
    filename2=filestump % ""
    df.to_csv(filename2, index=False)
    print(filename2)
    return filename1, filename2

def get_master_sheet_haupt(sheetID=RISKLAYER_MASTER_SHEET_20200521):
    df = download_sheet_table(sheetID=sheetID)
    files = save_csv_twice(df)


def add_urls_column(df):
    """
    combines all web sources into one column, as list
    """
    websources = ['Quelle 1', 'Gestrige Quellen', 'Quelle (Sollte nur Landesamt, Gesundheitsamt oder offiziell sein)', 'TWITTER', 'FACEBOOK/INSTAGRAM', 'Names']
    df["urls"]= [sorted(list(set( [url 
                            for url in urllist 
                            if url!=""] )))    # remove the nans
                 for urllist in df[websources].fillna("").values.tolist()] 
    return df

def load_master_sheet_haupt(filestump=HAUPT_FILES, timestamp="-20200520_211500"):
    filename =filestump % timestamp
    print ("Reading from", filename)
    df = pandas.read_csv(filename)
    sum=df["Fälle Heute bis 00Uhr"].sum()
    print ("Sum", sum, end=" ")
    lastEntry=pandas.to_datetime(df.Zeit).max()
    print ("Last entry was:", lastEntry)
    df=add_urls_column(df)
    print ("added urls column with all websources combined")
    
    df.index=df.AGS.tolist() 
    print("index == AGS, for easier access")
    return df


if __name__ == '__main__':
    
    # get_master_sheet_haupt(); exit() 
    # get_master_sheet_haupt(sheetID=RISKLAYER_MASTER_SHEET); exit()
    haupt = load_master_sheet_haupt(timestamp=""); exit()

    # downloadData(andStore=False); exit()

    # downloadData(); # exit()
    # load_data(); exit()

    # ts, bnn = data(withSynthetic=True)

    print()

    # TODO: Use 'datacolumns' instead of dropping
    # print (ts[ts["AGS"]=="00000"].drop(["AGS", "ADMIN"], axis=1).values.tolist())
    pass

    # df=get_wikipedia_landkreise_table(); 
    df=load_wikipedia_landkreise_table();
    print(df.describe()); print("sum:\n", df[["Einwohner", "Fläche"]].sum())
    print (df.to_string())
    print(df.loc[5370])
    
    