#!/usr/bin/env python3
"""
@summary: input data --> output data, misc helper functions

@version: v03.4 (24/June/2020)
@since:   26/April/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@param  AGS = https://de.wikipedia.org/wiki/Amtlicher_Gemeindeschl%C3%BCssel like riskLayer used it (4-5 digits)

@status:  Messy. Needs: (cleanup, function comments, solve TODOs, etc.)
          PERHAPS take apart, into several separate files?
          NOT yet: pretty, not at all easy to read, sorry. But it works.
"""
import copy
from dataclasses import dataclass

import datetime as dt
import numpy
import os
import pandas
from typing import List

import dataFiles


@dataclass
class DataMangled:
    """structure to hold the mangled overall covid data, gathered by `dataMangled()`"""
    ts: pandas.DataFrame = None
    """contains all districts with rows number 0,1,2,… and columns as follows:
        first column, 'AGS': 
            'Amtlicher Gemeindeschlüssel'='Community Identification Number', https://en.wikipedia.org/wiki/Community_Identification_Number#Germany)
            formatted with leading zero, if shorter than 5 characters
        second column, 'ADMIN': 
            name of the district, including its type in braces, e.g. 'district name (district type name)'
        remaining columns are ascending dates since 05.03.2020, up to newest, in format 'DD.MM.YYY': 
            number of cumulative Covid cases for the district up to that dates  
    """

    bnn: pandas.DataFrame = None
    """contains data from BNN with rows number 0,1,2,… and columns
        AGS: formatted *without* leading zero, if shorter than 5 characters
        GEN: district name
        BEZ: district type name
        Population: of district
        Infections: overall cumulative sum of Covid infections for district
        "Infections per 1000 population": …
        AGS_number: AGS again 	
        Infections_Bundesland: infections over all districts in the Bundesland (federal state) for the district
        Bundesland: Bundesland (federal state) for the district
        Population_Bundesland: population of district's federal state
        "Infections_Bundesland per 10000 population": overall cumulative sum of Covid infections for district's federal state
        Population: population of the district
    """
    ts_sorted: pandas.DataFrame = None
    """contains rows with AGS number as names and the columns:
        ADMIN: [see above]
        columns with ascending dates, like in `ts`
        Bundesland: [see above]
        Population: of district
        centerday: the 'expectation day' of all Covid cases for the district
        new_last14days: sum of district's new cases of the last 14 days
        new_last7days: sum of district's new cases of the last 7 days
        Reff_4_7_last: the news R_eff_4_7 value for the district (see `Reff_4_7()`)
    """
    Bundeslaender_sorted: pandas.DataFrame = None
    """like `ts_sorted`, but with federal state names as row names and values for the total federal state instead of district"""
    dates: List[dt.datetime] = None
    """list of datetime objects for ascending dates since 05.03.2020 up to newest"""
    datacolumns: pandas.Index = None
    """axis labels of dates out of `ts`"""


@dataclass
class District:
    """structure to hold the pandemic data of a german district ('Kreis'), which may be a single city or a region of several small once"""
    AGS: str
    """'Amtlicher Gemeindeschlüssel'='Community Identification Number' of the district, 
        https://en.wikipedia.org/wiki/Community_Identification_Number#Germany)"""

    bez: str
    """'Bezeichnung', type of district"""

    cumulative: List[int]
    """list of cumulative cases over all time, since 05.03.2020"""

    daily: List[int]
    """list of daily cases over all time, since 05.03.2020"""

    filename: str
    """filename for saving the generated plot/graph"""

    gen: str
    """name of the district"""

    inf: int
    """infections total of district"""

    inf_BL: int
    """infections total of the federal state ('Bundesland') the district lays in"""

    incidence_sum7: None
    """incidence sum of the last 7 days of the district's cases"""

    name_BL: str
    """name of the federal state ('Bundesland') the district lays in"""

    new_sum7: int
    """sum of new cases of last 7 days"""

    pop: int
    """population of district"""

    pop_BL: int
    """population of the federal state ('Bundesland') the district lays in"""

    reff_4_7: float
    """reff_4_7 value of district, calculated by `Reff_4_7`"""

    rolling_mean7: None
    """rolling mean of the last 7 days of the district's cases"""

    title: str
    """title string built from `gen`, `bez`, `ags`, `name_BL`, `pop`"""


districts = dict()
"""global dictionary to cache every `District`, which once has been gotten via `get_Kreis`"""

mangledData = DataMangled
"""global object to store the mangled main data once"""


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
    """
    please instead see below and use
    AGS_to_cumulative(ts_rich, datacolumns, AGS)
    """
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    return row.values[0][2:].tolist()


def AGS_to_ts_daily(ts, AGS):
    """
    please instead see below and use
    AGS_to_daily(ts_rich, datacolumns, AGS)
    """
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    
    # TODO: Use 'datacolumns' instead of dropping
    # print (row.drop(['AGS', 'ADMIN'], axis=1).columns); exit()
    row = row.drop(['AGS', 'ADMIN'], axis=1)
    # print(row.values); exit()
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

abbrev = {'Kreis': 'KR',
          'Kreisfreie Stadt' : 'KS',
          'Landkreis' : 'LK',
          'Stadtkreis': 'SK'}

def AGS_to_name_and_type(bnn, AGS):
    gen, bez, inf, pop = AGS_to_population(bnn, AGS)
    return "%s_%s" % (gen, abbrev[bez]) 


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
    multiplying height with index, and test_Reff(ts_sorted, datacolumns)dividing by sum of heights
    
    TODO: what to do with the negative values?
          Cut them out before summing perhaps?
          On the other hand, they (temporarily-)LOCALLY correct over-reported cases, right?
          So perhaps better to leave them in?
    """
    ddata = data[1:] # drop the nan in the first cell, i.e. shift left
    # print (ddata)
    productsum = sum([d*(i+1) for i,d in enumerate(ddata)]) # add one i.e. shift right
    center = productsum/sum(ddata) # + 1 - 1 # shift left and right equalize each other
    # synthetic "data" with one peak near center:
    signal = [0]*len(data)
    
    # TODO: this could also be a signal that the source data is errorenous.
    #       perhaps let it fail instead of this workaround to keep going?
    if center < 0:
        print ("ALERT: centerday index negative = %.2f" % center)
        center = 0 
    if int(round(center)) > len(data)-1:
        print ("ALERT: int(round(centerday)) index larger than array length = %.2f" % center)
        center = len(data)-1
    
    signal[int(round(center))]=max(ddata)*0.25
    return center, signal
    
    
def get_Kreis(dm: DataMangled, AGS):
    ags_int = int(AGS)
    if ags_int in districts:
        print('*'*12 + " returning known district from cache:", ags_int)
        dtr = districts[ags_int]
    else:
        dtr = District
        dtr.AGS = AGS
         # get data and names
        dtr.gen, dtr.bez, dtr.inf, dtr.pop = AGS_to_population(dm.bnn, AGS)
        dtr.name_BL, dtr.inf_BL, dtr.pop_BL = AGS_to_Bundesland(dm.bnn, AGS)
        dtr.title = "%s (%s #%s, %s) Population=%d" % (dtr.gen, dtr.bez, dtr.AGS, dtr.name_BL, dtr.pop)
        dtr.filename = "Kreis_" + ("00000" + dtr.AGS)[-5:] + ".png"
        dtr.daily = AGS_to_ts_daily(dm.ts, dtr.AGS)
        dtr.cumulative = AGS_to_ts_total(dm.ts, dtr.AGS)
        # TODO: calc incidence_sum7 here
        # TODO: calc rolling_mean7 here
        # TODO: calc new_sum7 here
        # TODO: calc reff_4_7 here
        # TODO: calc prevalence/1mio here   TODO: change prevalence to more commen per 100k
        # TODO: calc expectation day here
        # TODO: store 'info' flag symbol here
        districts[ags_int] = dtr
    return dtr.daily, dtr.cumulative, dtr.title, dtr.filename, dtr.pop


def join_tables_for_and_aggregate_Bundeslaender(ts, bnn):

    # careful, there might be more fields with nan (currently just the 3 copyright rows)
    ts_int = copy.deepcopy(ts.dropna())
    
    ts_int["AGS"]=pandas.to_numeric(ts_int["AGS"]) # must transform string to int, for merge:
    ts_BuLa = pandas.merge(ts_int, bnn[["AGS", "Bundesland", "Population"]], how="left", on=["AGS"])

    Bundeslaender=ts_BuLa.drop(["AGS"], axis=1).groupby(["Bundesland"]).sum()
    print("consistency check, does this look like Germany's population? ", Bundeslaender["Population"].sum())
    
    Bundeslaender.loc['Deutschland'] = Bundeslaender.sum().astype('int32').values.tolist()

    return ts_BuLa, Bundeslaender


def get_BuLa(Bundeslaender, name, datacolumns):
    # get data and names
    filename = "bundesland_" + name + ".png"
    population = Bundeslaender.loc[name, "Population"]
    # row = Bundeslaender.loc[Bundeslaender['Bundesland'] == name]
    
    row = Bundeslaender[datacolumns].loc[[name]]
    
    cumulative=row.values[0].tolist()
    diff = row.diff(axis=1)
    daily = diff.values[0].tolist()
    
    title = name + " Population=%d" % population
    
    return daily, cumulative, title, filename, population



def add_centerday_column(ts, ts_BuLa):
    
    ts_BuLa["centerday"] = [ temporal_center( AGS_to_ts_daily(ts, "%s" % AGS) )[0]
                            for AGS in ts_BuLa["AGS"].tolist() ]
    ts_sorted = ts_BuLa.sort_values("centerday", ascending=False).set_index("AGS")

    return ts_sorted

def add_centerday_column_Bundeslaender(Bundeslaender, datacolumns):
    Bundeslaender["centerday"] = [temporal_center(get_BuLa(Bundeslaender, name, datacolumns)[0])[0]
                                  for name in Bundeslaender.index.tolist() ]
    Bundeslaender.sort_values("centerday", ascending=False, inplace=True)
    return Bundeslaender


# def maxdata(ts_sorted):
#     maxvalue = max(ts_sorted[ts.columns[2:]].max())
#     digits=int(1 + numpy.log10(maxvalue))
#     return maxvalue, digits



def AGS_to_cumulative(ts_rich, datacolumns, AGS):
    """
    now also accepts tables with additional columns
    because positive selection by datacolumns (not negative by dropping columns)  
    """
    # print (ts_rich)
    # AGS = ("00000%s"%AGS)[-5:]
    # row = ts.loc[ts['AGS'] == AGS]
    # return row[datacolumns].values[0].tolist()
    return ts_rich.loc[AGS][datacolumns].tolist()


def AGS_to_daily(ts_rich, datacolumns, AGS):
    """
    now also accepts tables with additional columns
    because positive selection by datacolumns (not negative by droppping columns)  
    """
    cum = pandas.Series ( AGS_to_cumulative(ts_rich, datacolumns, AGS) ) 
    diff = cum.diff()
    return diff.values.tolist()

def cumulative_smoothed_last_week_incidence(cumulative, windowsize=7, daysBack=7):
    """
    experimental, not used yet
    'smoothed 1 week incidence'
    first averaging: 7 days rolling window, NOT centered, so that we have a result for today too
    then diff: look back 7 days 
    """
    averaged=pandas.DataFrame(cumulative).rolling(window=windowsize, center=False).mean()[0].values.tolist()
    return averaged[-1] - averaged[-daysBack-1]


def cumulative_today_minus_last_week_smoothed(cumulative, windowsize=7, daysBack=7):
    """
    'one week incidence smoothed'
    step 1: averaging with 7 days rolling window, AND centered!
    step 2: today's (UNSMOOTHED) value minus the SMOOTHED value 1 week ago
    """
    averaged=pandas.DataFrame(cumulative).rolling(window=windowsize, center=True).mean()[0].values.tolist()
    return cumulative[-1] - averaged[-daysBack-1]


def multiDayNewCases(cumulative, daysBack=7):
    """
    unaveraged, will probably work best for daysBack=7 or 14 or 21 
    """
    newCases = cumulative[-1] - cumulative[-daysBack-1]
    return newCases  


def add_weekly_columns(ts_rich, datacolumns):
    
    for days in (14, 7):
        ts_rich["new_last%ddays" % days] = [multiDayNewCases( AGS_to_cumulative(ts_rich, datacolumns, AGS), days)
                                           for AGS in ts_rich.index.values.tolist() ]
    return ts_rich


def BL_to_cumulative(Bundeslaender_rich, datacolumns, BL_name):
    """
    now also accepts tables with additional columns
    because positive selection by datacolumns (not negative by dropping columns)  
    """
    return Bundeslaender_rich.loc[BL_name][datacolumns].tolist()

def BL_to_daily(Bundeslaender_rich, datacolumns, BL_name):
    """
    can perhaps be replaced by AGS_to_daily because identical structure?
    """
    cum = pandas.Series ( BL_to_cumulative(Bundeslaender_rich, datacolumns, BL_name) ) 
    diff = cum.diff()
    return diff.values.tolist()



def add_weekly_columns_Bundeslaender(Bundeslaender, datacolumns):
    
    for days in (14, 7):
        colname = "new_last%ddays" % days
        Bundeslaender[colname] = [ multiDayNewCases(  BL_to_cumulative(Bundeslaender, datacolumns, name) , days)
                                  for name in Bundeslaender.index.tolist() ]

    return Bundeslaender


def Reff_4_4(daily,i):
    if i<7:
        return numpy.nan
    d=daily
    denominator = d[i-4]+d[i-5]+d[i-6]+d[i-7]
    result = (d[i]+d[i-1]+d[i-2]+d[i-3]) / denominator if denominator else numpy.nan
    return result 


def Reff_4_7(dailyNewCases, i=None):
    """
    Quotient of day (i) and day (i-4)
    
    but working on smoothed daily cases, with window length = 7 days.
     ( simple moving average, not centered around i, but all days up to i )
    
    If i is not given, assume i to be the very last day in the time series.
     ( corresponds to 3 days ago compared with 7 days ago, in 'centered' moving average)
    
    see https://heise.de/-4712676 for explanations
    """
    if not i:
        i=len(dailyNewCases)-1
    if i<10:
        return numpy.nan
    #                               # clip away negative values:
    d=pandas.DataFrame(dailyNewCases).clip(lower=0)[0].values.tolist()
    # print ("daily only positives:", d)
    
    avg_gen_size_now  =   ( d[i]  +d[i-1]+d[i-2]+d[i-3]+d[i-4]+d[i-5]+d[i-6] ) / 7.0
    avg_gen_size_before = ( d[i-4]+d[i-5]+d[i-6]+d[i-7]+d[i-8]+d[i-9]+d[i-10]) / 7.0
    Reff = avg_gen_size_now / avg_gen_size_before if avg_gen_size_before else numpy.nan
    return Reff 


def Reff_7_4(cumulative, i=None):
    """
    Quotient of weekly differences of totals ( x(i)-x(i-7) ) and ( x(i-7)-x(i-14) ).
    Then raised to the power 4/7, to transform the 7 days into 4 days generation time.  
    """
    if not i:
        i=len(cumulative)-1
    if i<14:
        return numpy.nan
    c=cumulative
    
    avg_gen_size_now  =   ( c[i] -  c[i-7] ) 
    avg_gen_size_before = ( c[i-7]-c[i-14] )
    Reff = (avg_gen_size_now / avg_gen_size_before)**(4/7) if avg_gen_size_before else numpy.nan
    return Reff 




def Reff_comparison(daily, cumulative, title, filename=None):
    daily_SMA=pandas.DataFrame(daily).rolling(window=7, center=True).mean()[0].values.tolist()
    daily_SMA
    # list(zip(cumulative,daily, daily_SMA))
    
    R1=[Reff_4_4(daily, i) for i, _ in enumerate(daily)]
    R2=[Reff_4_7(daily, i) for i, _ in enumerate(daily)]
    R3=[Reff_4_4(daily_SMA, i) for i, _ in enumerate(daily_SMA)]
    R4=[Reff_7_4(cumulative, i) for i, _ in enumerate(cumulative)]
    
    from matplotlib import pyplot as plt
    # matplotlib.pyplot.plot(R1)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(R1, label="Reff_4_4")
    ax.plot(R2, label="Reff_4_7")
    ax.plot(R3, label="Reff_4_4 on 7day-centered-SMA")
    ax.plot(R4, label="Reff_7_4")
    ax.legend()
    plt.title(title)
    
    if not filename:
        plt.show()
    else:
        fig.savefig(os.path.join(dataFiles.PICS_PATH, "R_experiments_" + filename),  bbox_inches='tight')
    
    print (Reff_4_7(daily), list(reversed(R2)))
    

def test_Reff_Kreis(ts_sorted, datacolumns):
    AGS=9377
    AGS=9479
    AGS=16076
    AGS=1061
    BL="Niedersachsen"
    print ("\nAGS")
    cumulative=ts_sorted.loc[AGS][datacolumns].tolist()
    print (list(reversed(cumulative)))
    # daily=ts_sorted.loc[AGS][datacolumns].diff().clip(lower=0).tolist()
    daily=ts_sorted.loc[AGS][datacolumns].diff().tolist()
    print (list(reversed(daily)))
    Reff_comparison(daily)
    
def test_Reff_BL(Bundeslaender, datacolumns, BL, filename=None):
    # BL="Niedersachsen"
    cumulative=Bundeslaender.loc[BL][datacolumns]
    daily=Bundeslaender.loc[BL][datacolumns].diff().tolist()
    Reff_comparison(daily, cumulative, title=BL, filename=filename)

def add_column_Kreise(ts_rich, datacolumns, inputseries=AGS_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7):

    ts_rich[operatorname] = [operator( inputseries(ts_rich, datacolumns, AGS) )
                             for AGS in ts_rich.index.values.tolist() ]
    return ts_rich


def add_column_Bundeslaender(Bundeslaender, datacolumns, inputseries=BL_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7):
    """
    can perhaps be replaced by add_column_Kreise because identical structure?
    """
    Bundeslaender[operatorname] = [ operator(  inputseries(Bundeslaender, datacolumns, name))
                                   for name in Bundeslaender.index.tolist() ]
    return Bundeslaender


def test_some_mangling():
    ts, bnn = dataFiles.data(withSynthetic=True)
    
    print (find_AGS(ts, "Osnabrück"))
    print (find_AGS(ts, "Heinsberg"))

    dates = dates_list(ts)

    AGS = "0"
    AGS = "1001"
    AGS = "5370"
    AGS = "9377"
    
    print ("AGS=%s" % AGS)
    print(AGS_to_ts_total(ts, AGS))
    print(AGS_to_ts_daily(ts, AGS))
    
    gen, bez, inf, pop = AGS_to_population(bnn, AGS)
    print (gen, bez, inf, pop)
    name, inf_BL, pop_BL = AGS_to_Bundesland(bnn, AGS)
    print (name, inf_BL, pop_BL )
    nameAndType = AGS_to_name_and_type(bnn, AGS)
    print (nameAndType )
    
    dailyIncrease = AGS_to_ts_daily(ts, "0")
    print (len(dailyIncrease))
    dailyIncrease = AGS_to_ts_daily(ts, "00000")
    print (len(dailyIncrease)) 
    
    center, signal = temporal_center(dailyIncrease)
    print ("expectation value at day %.2f" % center)
    # exit()

    dm = DataMangled
    dm.ts = ts
    dm.bnn = bnn

    print ("\nKreis")
    daily, cumulative, title, filename, pop = get_Kreis(dm, AGS)
    print (daily, cumulative)
    print (title, filename, pop)
    
    print ("\nBundesländer")
    ts_BuLa, Bundeslaender = join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    
    # ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled(withSynthetic=withSyntheticData)
    dm = dataMangled()
    
    daily, cumulative, title, filename, population = get_BuLa(Bundeslaender, "Hessen", dm.datacolumns)
    print (daily, cumulative)
    print (title, filename, population)
    
    # print ( maxdata(ts_sorted) )
    # total_max_cum, digits = maxdata(ts_sorted)
    
    AGS = 0
    AGS=1001
    AGS=5370
    print (AGS_to_cumulative(ts_rich=dm.ts_sorted, datacolumns=dm.datacolumns, AGS=AGS))
    print (AGS_to_daily(ts_rich=dm.ts_sorted, datacolumns=dm.datacolumns, AGS=AGS))

    cumulative=AGS_to_cumulative(ts_rich=dm.ts_sorted, datacolumns=dm.datacolumns, AGS=AGS)
    print (cumulative_smoothed_last_week_incidence(cumulative))
    print (cumulative_today_minus_last_week_smoothed(cumulative))
    print (multiDayNewCases(cumulative))
    print (multiDayNewCases(cumulative, 14))
    print (multiDayNewCases( AGS_to_cumulative(dm.ts_sorted, dm.datacolumns, AGS) , 14) )
    print (dm.ts_sorted.loc[AGS][["new_last14days", "new_last7days"]]); # exit()
    print (dm.ts_sorted["new_last14days"][AGS]);
    
    # print (add_weekly_columns_Bundeslaender(Bundeslaender_sorted, datacolumns))
    print (add_weekly_columns_Bundeslaender(dm.Bundeslaender_sorted, dm.datacolumns)[["new_last14days", "new_last7days"]])
    
    # test_Reff_Kreis(ts_sorted, datacolumns)
    # test_Reff_BL(Bundeslaender_sorted, datacolumns, BL="Hamburg")
    
    for BL in dm.Bundeslaender_sorted.index:
        test_Reff_BL(dm.Bundeslaender_sorted, dm.datacolumns, BL=BL, filename=BL+".png")
    
    
def additionalColumns(ts,bnn):
    """
    this can operate on data in RAM
    """
    dates = dates_list(ts)
    datacolumns = ts.columns[2:]
    print ("\nNewest column = '%s'" % datacolumns[-1])
    ts_BuLa, Bundeslaender = join_tables_for_and_aggregate_Bundeslaender(ts, bnn)

    ts_sorted = add_centerday_column(ts, ts_BuLa)
    ts_sorted = add_weekly_columns(ts_sorted, datacolumns)
    ts_sorted = add_column_Kreise(ts_sorted, datacolumns, inputseries=AGS_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7)

    Bundeslaender_sorted = add_centerday_column_Bundeslaender(Bundeslaender, datacolumns)
    Bundeslaender_sorted = add_weekly_columns_Bundeslaender(Bundeslaender_sorted, datacolumns)
    Bundeslaender_sorted = add_column_Bundeslaender(Bundeslaender_sorted , datacolumns, inputseries=BL_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7)

    ts_sorted["new_last14days"] = ts_sorted["new_last14days"].astype(int)
    ts_sorted["new_last7days"] = ts_sorted["new_last7days"].astype(int)
    Bundeslaender_sorted["new_last14days"] = Bundeslaender_sorted["new_last14days"].astype(int)
    Bundeslaender_sorted["new_last7days"] = Bundeslaender_sorted["new_last7days"].astype(int)

    for datecol in datacolumns:
        ts_sorted[datecol]=ts_sorted[datecol].astype(int)
        Bundeslaender_sorted[datecol]=Bundeslaender_sorted[datecol].astype(int)

    return  ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns

def dataMangled(withSynthetic=True, ifPrint=True):
    """
    this loads from disk first
    """
    global mangledData
    if mangledData.ts is not None:
        return mangledData

    ts, bnn = dataFiles.data(withSynthetic=withSynthetic, ifPrint=ifPrint)

    mangledData = DataMangled(*additionalColumns(ts,bnn))

    return mangledData



if __name__ == '__main__':
    test_some_mangling(); exit()
    
    # ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangled(withSynthetic=True)
    
