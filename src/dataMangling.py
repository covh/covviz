'''
Created on 26 Apr 2020

@author: andreas

@param  AGS = https://de.wikipedia.org/wiki/Amtlicher_Gemeindeschl%C3%BCssel like riskLayer used it (4-5 digits)
 
'''

import os, copy
import datetime as dt
import pandas, numpy, matplotlib
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
    ts_BuLa = pandas.merge(ts_int, bnn[["AGS", "Bundesland", "Population"]], how="left", on=["AGS"])

    Bundeslaender=ts_BuLa.drop(["AGS"], axis=1).groupby(["Bundesland"]).sum()
    print("consistency check, does this look like Germany's population? ", Bundeslaender["Population"].sum())
    
    Bundeslaender.loc['Deutschland'] = Bundeslaender.sum().astype('int32').values.tolist()

    return ts_BuLa, Bundeslaender


def get_BuLa(Bundeslaender, name):
    # get data and names
    filename = "bundesland_" + name + ".png"
    population = Bundeslaender.loc[name, "Population"]
    # row = Bundeslaender.loc[Bundeslaender['Bundesland'] == name]
    
    
    # TODO: Use 'datacolumns' instead of dropping 
    row = Bundeslaender.drop(["Population"], axis=1).loc[[name]]
    
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

def add_centerday_column_Bundeslaender(Bundeslaender):
    Bundeslaender["centerday"] = [temporal_center(get_BuLa(Bundeslaender, name)[0])[0]
                                  for name in Bundeslaender.index.tolist() ]
    Bundeslaender.sort_values("centerday", ascending=False, inplace=True)
    return Bundeslaender


def maxdata(ts_sorted):
    maxvalue = max(ts_sorted[ts.columns[2:]].max())
    digits=int(1 + numpy.log10(maxvalue))
    return maxvalue, digits



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

def Reff_4_7(daily,i=None):
    """
    quotient of day (i) with day (i-4), but working on smoothed data:
    simple moving average, not centered, window of days = 7
    
    if no i given, assume it to be the very last day.
    """
    if not i:
        i=len(daily)-1
    if i<10:
        return numpy.nan
    d=daily
    denominator = d[i-4]+d[i-5]+d[i-6]+d[i-7]+d[i-8]+d[i-9]+d[i-10]
    result =       (d[i]+d[i-1]+d[i-2]+d[i-3]+d[i-4]+d[i-5]+d[i-6]) / denominator if denominator else numpy.nan
    return result 




def Reff_comparison(daily):
    daily_SMA=pandas.DataFrame(daily).rolling(window=7, center=True).mean()[0].values.tolist()
    daily_SMA
    # list(zip(cumulative,daily, daily_SMA))
    
    R1=[Reff_4_4(daily, i) for i, _ in enumerate(daily)]
    R2=[Reff_4_7(daily, i) for i, _ in enumerate(daily)]
    R3=[Reff_4_4(daily_SMA, i) for i, _ in enumerate(daily_SMA)]
    
    R1
    from matplotlib import pyplot as plt
    # matplotlib.pyplot.plot(R1)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(R1, label="Reff_4_4")
    ax.plot(R2, label="Reff_4_7")
    ax.plot(R3, label="Reff_4_4 on 7day-centered-SMA")
    ax.legend()
    plt.show()
    
    print (Reff_4_7(daily), list(reversed(R2)))
    

def test_Reff_Kreis(ts_sorted, datacolumns):
    AGS=9377
    AGS=9479
    AGS=16076
    BL="Niedersachsen"
    cumulative=ts_sorted.loc[AGS][datacolumns].tolist()
    daily=ts_sorted.loc[AGS][datacolumns].diff().tolist()
    Reff_comparison(daily)
    
def test_Reff_BL(Bundeslaender, datacolumns, BL):
    # BL="Niedersachsen"
    daily=Bundeslaender.loc[BL][datacolumns].diff().tolist()
    Reff_comparison(daily)


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


def dataMangled(withSynthetic=True):
    ts, bnn = dataFiles.data(withSynthetic=withSynthetic)
    dates = dates_list(ts)
    datacolumns = ts.columns[2:]
    ts_BuLa, Bundeslaender = join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    ts_sorted = add_centerday_column(ts, ts_BuLa)
    ts_sorted = add_weekly_columns(ts_sorted, datacolumns)
    ts_sorted = add_column_Kreise(ts_sorted, datacolumns, inputseries=AGS_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7)
    Bundeslaender_sorted = add_centerday_column_Bundeslaender(Bundeslaender)
    Bundeslaender_sorted = add_weekly_columns_Bundeslaender(Bundeslaender_sorted, datacolumns)
    Bundeslaender_sorted = add_column_Bundeslaender(Bundeslaender_sorted , datacolumns, inputseries=BL_to_daily, operatorname="Reff_4_7_last", operator=Reff_4_7)
    return ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns



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
    nameAndType = AGS_to_name_and_type(bnn, AGS)
    print (nameAndType ); # exit()
    
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
    
    # print ( maxdata(ts_sorted) )
    # total_max_cum, digits = maxdata(ts_sorted)

    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangled(withSynthetic=True)
    AGS = 0
    AGS=1001
    AGS=5370
    print (AGS_to_cumulative(ts_rich=ts_sorted, datacolumns=datacolumns, AGS=AGS))
    print (AGS_to_daily(ts_rich=ts_sorted, datacolumns=datacolumns, AGS=AGS))

    cumulative=AGS_to_cumulative(ts_rich=ts_sorted, datacolumns=datacolumns, AGS=AGS)
    print (cumulative_smoothed_last_week_incidence(cumulative))
    print (cumulative_today_minus_last_week_smoothed(cumulative))
    print (multiDayNewCases(cumulative))
    print (multiDayNewCases(cumulative, 14))
    print (multiDayNewCases( AGS_to_cumulative(ts_sorted, datacolumns, AGS) , 14) )
    print (ts_sorted.loc[AGS][["new_last14days", "new_last7days"]]); # exit()
    print (ts_sorted["new_last14days"][AGS]);
    
    # print (add_weekly_columns_Bundeslaender(Bundeslaender_sorted, datacolumns))
    print (add_weekly_columns_Bundeslaender(Bundeslaender_sorted, datacolumns)[["new_last14days", "new_last7days"]])
    
    # test_Reff_Kreis(ts_sorted, datacolumns)
    test_Reff_BL(Bundeslaender_sorted, datacolumns, BL="Thüringen")
    
    
    