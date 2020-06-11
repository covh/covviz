'''
Created on 25 Apr 2020

@author: andreas
'''

import os, shutil, hashlib, time
import pandas, wget, requests, numpy
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


def swap_specific_typo_cells(df, correct_type, wrong='o', correct='0'):
    """
    Every few days, riskLayer makes another typo in the CSV file. 
    
    This is hopefully useful as an abstraction to fix that faster in future cases.
    It will always need manual interaction but this should speed it up.
    
    1 search for any occurence of 'o'
    2 go through all rows (indices) affected
    3 find the specific columns with 'o'
    4 correct the data, by overwriting with '0'
    5 cast all those affected columns to <class 'numpy.float64'>
    6 return a corrected dataframe, and the rows - if the latter is empty, nothing had happened.
    """
    
    print("Searching for '%s' instead of '%s':" %(wrong, correct))
    typos = df[df.astype(str).eq(wrong).any(1)]
    affected_cols=[]
    for i in typos.index:
        print ("row index", i)
        cols=df.columns[df.loc[i].astype(str)==wrong].tolist()
        # print(cols)
        for col in cols:
            print(col, ":", df.loc[i,col], end=" --> ")
            df.loc[i,col]=correct
            print(df.loc[i,col])
        affected_cols.extend(cols)
    
    if affected_cols:
        print ("Done. Now casting affected columns %s to %s" % (affected_cols, correct_type))
        for col in affected_cols:
            df[col]=df[col].astype(correct_type)
        
    return df, affected_cols

        
def testing_swap_specific_typo_cells():
    df=pandas.read_csv(TS_NEWEST, encoding='cp1252')
    
    print("\ndefault example with 'o' instead of '0':")
    swap_specific_typo_cells(df, correct_type=type(df.loc[1, "01.06.2020"]))
    
    print("\nexample with 'docs' instead of '0':")
    df, cols=swap_specific_typo_cells(df, correct_type=type(df.loc[1, "01.06.2020"]), wrong='docs', correct=0)
    if not cols:
        print("Looks like they've repaired it.")
    
    print("\nexample with several findings:")
    swap_specific_typo_cells(df, correct_type=type(df.loc[1, "01.06.2020"]), wrong='601.0', correct=601.0)


def show_problematic_columns(df, type_wanted=numpy.float64, how_many_different=2):
    cols = df.columns[df.dtypes!=type_wanted].tolist()
    if len(cols)>how_many_different:
        print("There are columns which are not '%s': %s" % (type_wanted, cols))
        


def repairData(ts, bnn):
    """
    The CSV contains data typos every few days.
    This will only get better when they automate the procedure to create the CSV, see their "Fragen und Antworten" sheet.
    These problems are patched here:
    
    12.03.20203
    ï»¿AGS
    1733.0  -->   1.739  -->  1743.0
    'docs'
    'o'
    """
    
    print ("\nRepair dirty risklayer data:")
    
    show_problematic_columns(ts)
    
    
    newcols = ["12.03.2020" if x=="12.03.20203" else x for x in ts.columns]
    if newcols!=ts.columns.tolist():
        print ("found and fixed 12.03.20203 --> 12.03.2020 (problem since 25/4/2020)")
    
    newcols2 = ["AGS" if x=='ï»¿AGS' else x for x in newcols]
    if newcols2!=newcols:
        print ("found and fixed ï»¿AGS --> AGS  (problem since 29/4/2020)")
        
    ts.columns = newcols2
    

    before = ts[ts["AGS"]=="05370"]["27.04.2020"]
    after  = ts[ts["AGS"]=="05370"]["28.04.2020"]
    # print (float(after) / float(before) ) 
    if float(after) / float(before) < 0.5:
        print ("huge drop of some values for 28.4.2020, e.g. Heinsberg: 1733.0  -->   1.739  -->  1743.0 (was a problem on 29/4/2020)")
        print ("temporary fix: interpolate 28. from 27. and 29.")
        ts["28.04.2020"]=(ts["29.04.2020"]+ts["27.04.2020"])/2

    
    # print (ts.index.tolist()); exit()
    colproblem, colgood= "10.03.2020", "09.03.2020"
    
    typo='docs' # problem appeared in 25.05.2020 file:
    ii=ts[ts[colproblem].astype(str)==typo].index.values.tolist()
    # print(ii)
    if ii:
        print ("found typo '%s' in datafile at positions [%s, %s] (was a problem on 25/5/2020)" % (typo, ii, colproblem), end=" ")
        if len(ii)>1:
            raise Exception("ALARM: SEVERAL")
        i=ii[0]
        # print(ts.loc[i,"10.03.2020"])
        ts.loc[i,colproblem]=ts.loc[i,colgood]
        # print(ts.loc[i,"10.03.2020"])
        
        # ts=ts.drop([401, 402, 403])
        print ("overwritten with previous day value. Now cast whole column to 'float':", end=" ")
        ts[colproblem]=ts[colproblem].astype(float)
        print ("Done.")

    
    wrong, correct='o',0 # typo 'o' instead of 0
    df, cols = swap_specific_typo_cells(ts, correct_type=type(ts.loc[1, "01.06.2020"]), wrong=wrong, correct=correct)
    if cols:
        print("found and fixed typo '%s' which had cast whole column/s %s to string. Corrected that now. (appeared on June 2nd 2020)" % (wrong, cols))
        ts=df
    else:
        print("They fixed that problem (which had appeared on June 2nd).")
    
    # perhaps there are still columns that need fixing:
    show_problematic_columns(ts)
    
    # print ("Still unfixed: 10000 --> 1000 in bnn!k2 (i.e. fixed manually)") # solved in source table
    print()
    return ts, bnn


def pandas_settings_full_table():
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 200)
    pandas.set_option('display.max_rows', None)


def inspectNewestData(ts):
    ts, _ = repairData(ts, [])
    
    # print (ts.columns)
    lastColumns=["ADMIN"] + ts.columns[-5:].tolist()
    df = ts[lastColumns]
    print ("\nJust visual inspection - unless the following tables get VERY LONG - all is probably good ...\n(TODO: Automate this with two thresholds (number of, amount of drop)?)\n")
    
    pandas_settings_full_table()
    
    # TODO: 
    # when this became 91 rows, with sometimes > 1500 cases dropped
    # it helped to find out that the source data was errorenous.
    # perhaps in the future, let the script fail? Send an email to admin?
    # for now it simply prints an ALERT, but only by number of rows
    # and not yet by total negative diff.
    down_prev=df[df[lastColumns[-2]]<df[lastColumns[-3]]]
    if len(down_prev)>20:
        print (("*"*100 + "\n")*3)
        print ("ALERT: Alarmingly many - ", end=" ")
    print ("%d values going DOWN for previous day:" % len(down_prev))
    time.sleep(2)
    if len(down_prev):
        print (down_prev)
    print()
    
    down_last=df[df[lastColumns[-1]]<df[lastColumns[-2]]]
    if len(down_last)>20:
        print ("ALERT: Alarmingly many - ", end=" ")
    print ("%d values going DOWN for newest day:" % len(down_last))
    time.sleep(2)
    if len(down_last):
        print (down_last)
    print()
    
    print()
    print ("Totals:")
    datecolumns=ts.columns[-9:].tolist()
    df = ts[datecolumns].sum()
    # df["diff"]=df.diff()
    print (df.astype(int).to_string())
    print ("Diffs:")
    print (df.diff().dropna().astype(int, errors='ignore').to_string())
    # print (df)
    
def hash_file(filename):
    with open(filename,"rb") as f:
        allbytes = f.read() # read entire file as bytes
        readable_hash = hashlib.sha256(allbytes).hexdigest();
    # print(readable_hash)
    return readable_hash
    
def true_if_exist_and_equal(filenames):
    if len(filenames)<2:
        raise Exception("must compare more than one file.") 
    hashes=[]
    for filename in filenames:
        try:
            hashes.append(hash_file(filename))
        except Exception as e:
            print(type(e), e) # TOO: perhaps comment away?
            print ("didn't exist, means new data available, downloaded, and stored:")
            return False
    unique=list(set(hashes)) 
    return len(unique)==1

def test_comparison():
    for filenames in [["test1.txt", "test2.txt"], ["test1.txt", "test3.txt"]]: 
        print (filenames, true_if_exist_and_equal(filenames))

def downloadData(andStore=True):

    print (RISKLAYER_URL01)
    filename = wget.download(RISKLAYER_URL01, out=DATA_PATH)
    print ("downloaded:", filename)

    ts=pandas.read_csv(filename, encoding='cp1252') # encoding='utf-8')
    last_col = ts.columns[2:].tolist()[-1]
    print ("newest column:", last_col)
    
    d=last_col.split(".")
    d.reverse()
    last_date = "".join(d)
    newfilename = TS_FILE.replace("20200425", last_date)
    equal = true_if_exist_and_equal([filename, newfilename])

    if andStore:
        print ("Saving into files:")
        shutil.move(filename, newfilename)
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

    # Say if a new file was created. Also return the dataFrame itself, for use on readonly filesystem (heroku):
    return not equal, ts


def get_wikipedia_landkreise_table(url='https://de.wikipedia.org/wiki/Liste_der_Landkreise_in_Deutschland', 
                                   filename=WP_FILE):
    
    """
    todo: the same for https://de.wikipedia.org/wiki/Liste_der_kreisfreien_St%C3%A4dte_in_Deutschland
    """

    print ("\nscrape wikipedia page:")

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


def load_data(ts_f=TS_NEWEST, bnn_f=BNN_FILE, ifPrint=True):
    ts=pandas.read_csv(ts_f, encoding='cp1252') # encoding='utf-8')
    bnn=pandas.read_csv(bnn_f)
    print ("\nLoading data from RiskLayer. This is their message:")
    print ("\n".join(ts[ts.ADMIN.isna()][ts.columns[0]].tolist()))
    print()
    # now drop those info lines which are not data:
    ts.drop(ts[ts.ADMIN.isna()].index, inplace=True)
    ts, bnn = repairData(ts, bnn)
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

def data(withSynthetic=True, ifPrint=True):
    ts, bnn = load_data(ifPrint=ifPrint)
    if withSynthetic:
        ts, bnn = add_synthetic_data(ts, bnn)
    return ts, bnn


def download_sheet_table(sheetID=RISKLAYER_MASTER_SHEET, table=RISKLAYER_MASTER_SHEET_TABLE, reindex="AGS"):
    risklayer_sheet_url = GOOGLEDOCS_ToCSV_WithSheetname % (sheetID, table[1], table[0])
    print ("Downloading this data:")
    print (risklayer_sheet_url)
    df=pandas.read_csv(risklayer_sheet_url) # error_bad_lines=False)
    if reindex:
        df.index=df[reindex].tolist() # index == AGS, easier accessprint("to_datetimes\n", to_datetimes)
    #print(df.columns.tolist())
    return df
    
def save_csv_twice(df, filestump=HAUPT_FILES):
    
    pandas_settings_full_table()
    # print ("df.Zeit\n", df.Zeit)
    
    # became more complicated on June 1st because pandas read 01/06/2020 as 6th of January. The dropna is probably not needed? But anyways, we focus on the newest date only so typos don't matter....
    to_datetimes = pandas.to_datetime(df.Zeit, format="%d/%m/%Y %H:%M", errors='coerce')
    # print("to_datetimes\n", to_datetimes)
    #print("to_datetimes dropna\n", to_datetimes.dropna())
    to_datetimes_strings = to_datetimes.dropna().dt.strftime("%Y%m%d_%H%M%S")
    #print("to_datetimes_strings", to_datetimes_strings)  
    lastEntry = to_datetimes_strings.max()
    print ("Newest entry was:", lastEntry)
    
    timestamp=lastEntry
    filename1=filestump % ("-" + timestamp)
    existed = os.path.isfile(filename1)
    df.to_csv(filename1, index=False)
    print(filename1)
    filename2=filestump % ""
    df.to_csv(filename2, index=False)
    print(filename2)
    return existed, (filename1, filename2)

def get_master_sheet_haupt(sheetID=RISKLAYER_MASTER_SHEET_20200521):
    """
    TODO: catch exceptions, then return False
    """
    df = download_sheet_table(sheetID=sheetID)
    existed, files = save_csv_twice(df)
    return not existed


def add_urls_column(df, hauptversion="v02"):
    """
    combines all web sources into one column, as list
    """
    print (df.columns); exit()
    quellenspalten={"v01": ['Quelle 1', 'Gestrige Quellen', 'Quelle (Sollte nur Landesamt, Gesundheitsamt oder offiziell sein)', 'TWITTER', 'FACEBOOK/INSTAGRAM', 'Names'],
                    "v02": ['Quelle 1',                     'Quelle (Sollte nur Landesamt, Gesundheitsamt oder offiziell sein)', 'TWITTER', 'FACEBOOK/INSTAGRAM', 'Names'] }
    websources = quellenspalten[hauptversion] 
    df["urls"]= [sorted(list(set( [url 
                            for url in urllist 
                            if url!="" and url!="nn"] )))    # remove the nans
                 for urllist in df[websources].fillna("").values.tolist()] 
    return df

def load_master_sheet_haupt(filestump=HAUPT_FILES, timestamp="-20200520_211500", hauptversion="v02"):
    filename =filestump % timestamp
    print ("Reading from", filename)
    df = pandas.read_csv(filename)
    daysum=df["Fälle Heute bis 00Uhr"].sum()
    print ("Sum", daysum, end=" ")
    lastEntry=pandas.to_datetime(df.Zeit).max()
    print ("Last entry was:", lastEntry)
    df=add_urls_column(df, hauptversion=hauptversion)
    print ("added urls column with all websources combined")
    
    df.index=df.AGS.tolist() 
    print("index = AGS, for easier access")
    return df

def scrape_and_test_wikipedia_pages():
    get_wikipedia_landkreise_table();
    df=load_wikipedia_landkreise_table();
    print("\ndescribe:\n%s" % df.describe())
    print("\nsum:\n%s" % df[["Einwohner", "Fläche"]].sum().to_string())
    print("\nexample:\n %s" % df.loc[5370].to_string())
    return df
    

if __name__ == '__main__':
    # testing_swap_specific_typo_cells(); exit()
    # test_comparison(); exit()
    
    # get_master_sheet_haupt(); exit() 
    # get_master_sheet_haupt(sheetID=RISKLAYER_MASTER_SHEET); exit() 
    # haupt = load_master_sheet_haupt(timestamp=""); exit()
    # equal, ts = downloadData(andStore=False);


    # newData, ts = downloadData(); print ("\ndownloaded timeseries CSV was new:", newData); exit()


    downloadData(); exit()
    load_data(); exit()

    # ts, bnn = data(withSynthetic=True)

    print()

    # TODO: Use 'datacolumns' instead of dropping
    # print (ts[ts["AGS"]=="00000"].drop(["AGS", "ADMIN"], axis=1).values.tolist())
    pass

    df=scrape_and_test_wikipedia_pages()
    # print (df.to_string())

