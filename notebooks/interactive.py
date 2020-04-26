#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas
import numpy
from matplotlib import pyplot as plt
import matplotlib 


# In[ ]:


DATA_PATH = os.path.join("..", "data")
BNN_FILE = os.path.join(DATA_PATH, "GermanyKreisebene_Risklayer_bnn-20200425.csv")
TS_FILE =  os.path.join(DATA_PATH, "GermanyValues_RiskLayer-20200425.csv")
PICS_PATH = os.path.join(DATA_PATH, "..", "pics")
PAGES_PATH = os.path.join(DATA_PATH, "..", "pages")


# In[ ]:


def load_data(ts_f=TS_FILE, bnn_f=BNN_FILE):
    ts=pandas.read_csv(ts_f)
    bnn=pandas.read_csv(bnn_f)
    return ts, bnn
ts, bnn = load_data()

synthetic_data = [0]*10 + [20,80,100] + [100] * (len(ts.columns)-2-10-3)
row = pandas.Series(["00000", "Dummykreis"]+synthetic_data, index=ts.columns)
ts=ts.append(row, ignore_index=True)

synthetic_landkreis = [0, "Dummykreis", "Landkreis", 150000, 100, 0.67, 0, 300,"Dummyland", 400000, 0.75]
row = pandas.Series(synthetic_landkreis, index=bnn.columns)
bnn=bnn.append(row, ignore_index=True)


# In[ ]:


bnn


# In[ ]:


def find_AGS(name):
    cond = ts['ADMIN'].str.contains(name, na=False)
    # return cond
    rows = ts.loc[cond]
    return rows
find_AGS("Osnabrück")
find_AGS("Heinsberg")


# In[ ]:


import datetime as dt
def to_dt(dt_str):
    d = list(map(int, dt_str.split(".")))
    # print(d)
    return dt.datetime(d[2], d[1], d[0])

dates=[to_dt(d) for d in ts.columns[2:].values]
print (dates)
# ts.values[0]


# In[ ]:


def AGS_to_ts_total(AGS):
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    return row.values[0][2:].tolist()
    
AGS = "0"
AGS = "1001"
AGS_to_ts_total(AGS)


# In[ ]:


def AGS_to_ts_daily(AGS):
    AGS = ("00000"+AGS)[-5:]
    row = ts.loc[ts['AGS'] == AGS]
    row = row.drop(['AGS', 'ADMIN'], axis=1)
    # return row
    diff = row.diff(axis=1)
    return diff.values[0].tolist()
    
AGS="0"
#AGS="5370"
print(AGS_to_ts_daily(AGS))


# In[ ]:


def AGS_to_population(AGS):
    # AGS = ("00000"+AGS)[-5:]
    AGS = int(AGS)
    # print(AGS)
    row = bnn.loc[bnn['AGS'] == AGS]
    pop = row["Population"].values[0] 
    inf = row["Infections"].values[0] 
    gen = row["GEN"].values[0] 
    bez = row["BEZ"].values[0] 
    return gen, bez, inf, pop
def AGS_to_Bundesland(AGS):
    # AGS = ("00000"+AGS)[-5:]
    AGS = int(AGS)
    row = bnn.loc[bnn['AGS'] == AGS]
    name = row["Bundesland"].values[0] 
    inf_BL = row["Infections_Bundesland"].values[0] 
    pop_BL = row["Population_Bundesland"].values[0] 
    return name, inf_BL, pop_BL

AGS="0"
#AGS="1001"
print (AGS_to_population(AGS)) 
print(AGS_to_Bundesland(AGS))


# In[ ]:


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
    
data = AGS_to_ts_daily("00000")
# print (data)
center, signal = temporal_center(data)
print ("center at day %.2f" % center)
    


# In[ ]:


def plot_timeseries(dates, daily, cumulative, title, filename):

    fig, ax = plt.subplots(figsize=(14, 10)) #, constrained_layout=True)
    # plt.tight_layout()

    # x axis
    ax.xaxis_date()
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
    fig.autofmt_xdate(rotation=45)


    # plot data
    lns1 = ax.plot(dates, daily, label="daily cases", color='lightgray')
    plt.ylabel("daily cases", color="black")
    plt.ylim(0, max(daily[1:])*1.5)

    # plot averages
    window=7
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    lns2 = ax.plot(dates, rolling_mean, label='daily: SMA %s days' % window, color='purple')

    window=14
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    lns3 = ax.plot(dates, rolling_mean, label='daily: SMA %s days' % window, color='orange', linewidth=4)

    # window=21
    # rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    # ax.plot(dates, rolling_mean, label='SMA %s days' % window, color='pink', linewidth=1)

    # plot center bar
    center, signal = temporal_center(daily)
    center_date=ts.columns[2:].values[int(round(center))]
    lns4 = ax.bar(dates, signal, label="'center day': "+center_date, color='green')
    # lns4 = ax.plot(dates, signal, label="'center day': "+center_date, color='green', kind='bar')


    # plot 2nd axis and cumulative data
    ax2 = plt.twinx()
    plt.ylim(0, max(cumulative)*1.1)
    plt.ylabel("cumulative total cases", color="b")

    lns5 = ax2.plot(dates, cumulative, label="total cases", color = 'b')

    lines = lns5 + lns1 + lns2 + lns3
    labs = [l.get_label() for l in lines]

    plt.legend(lines, labs, loc='best', facecolor="white", framealpha=1, 
               title="'center date' = "+center_date)

    plt.title(title)
    plt.show()
    
    fig.savefig(os.path.join(PICS_PATH, filename),  bbox_inches='tight')

    
def get_Kreis(AGS):
    # get data and names
    gen, bez, inf, pop = AGS_to_population(AGS)
    title = "%s (%s) AGS %s" % (gen, bez, AGS)
    filename = "Kreis_" + ("00000"+AGS)[-5:] + ".png"
    daily = AGS_to_ts_daily(AGS)
    cumulative = AGS_to_ts_total(AGS)
    return daily, cumulative, title, filename
# print (cumulative)

AGS = "00000"
# AGS = "5370"
AGS = "1001"
AGS="9377"

daily, cumulative, title, filename = get_Kreis(AGS)
plot_timeseries(dates, daily, cumulative, title, filename=filename)


# In[ ]:


import copy
ts_int = copy.deepcopy(ts.dropna()) # careful, there might be more fields with na but just the 3 copyright rows
ts_int["AGS"]=pandas.to_numeric(ts_int["AGS"]) # must transform string to int, for merge:
ts_BuLa=pandas.merge(ts_int, bnn[["AGS", "Bundesland", "Population"]], how="left", on=["AGS"])
ts_BuLa


# In[ ]:


Bundeslaender=ts_BuLa.drop(["AGS"], axis=1).groupby(["Bundesland"]).sum()
print(Bundeslaender["Population"].sum())
Bundeslaender


# In[ ]:


#Bundeslaender.drop(["Population"], axis=1).loc['Hessen'].to_list()


# In[ ]:


def get_BuLa(name):
    # get data and names
    title = name
    filename = "bundesland_" + name + ".png"
    population = Bundeslaender.loc['Hessen', "Population"]
    # row = Bundeslaender.loc[Bundeslaender['Bundesland'] == name]
    row = Bundeslaender.drop(["Population"], axis=1).loc[[name]]
    
    cumulative=row.values[0].tolist()
    diff = row.diff(axis=1)
    daily = diff.values[0].tolist()
    
    return daily, cumulative, title, filename, population

daily, cumulative, title, filename, population = get_BuLa("Hessen")
[title, filename, population, daily, cumulative]


# In[ ]:


daily, cumulative, title, filename, population = get_BuLa("Bayern")
plot_timeseries(dates, daily, cumulative, title, filename=filename)


# In[ ]:


for BL in Bundeslaender.index.tolist():
    daily, cumulative, title, filename, population = get_BuLa(BL)
    plot_timeseries(dates, daily, cumulative, title, filename=filename)


# In[ ]:


ts_BuLa["centerday"] = [ temporal_center( AGS_to_ts_daily("%s" % AGS) )[0] for AGS in ts_BuLa["AGS"].tolist() ]
ts_sorted=ts_BuLa.sort_values("centerday").set_index("AGS")


# In[ ]:


def maxdata(ts_sorted):
    maxvalue = max(ts_sorted[ts.columns[2:]].max())
    digits=int(1+numpy.log10(maxvalue))
    return maxvalue, digits

maxdata(ts_sorted)


# In[ ]:


ts_sorted["centerday"][1001]


# In[ ]:


def toHTMLRow_diffmean(AGS, digits, cmap, labels):
    row = ts_sorted[ts.columns[2:]].loc[AGS].astype('int')
    diff= pandas.DataFrame(row).diff(axis=0)[AGS].tolist()
    diff[0]=0 # overwrite the nan
    diff=list(map(int, diff)) #make integer
    
    window=14
    rolling_mean_diff = pandas.DataFrame(diff).rolling(window=window, center=True).mean().fillna(0)[0].tolist()
    # return rolling_mean_diff
    
    cumulative=row.tolist()
    # return diff, cumulative
    cummax, diffmax, rollingdiffmax = max(cumulative), max(diff), max(rolling_mean_diff)
    # return cummax, diffmax, rollingdiffmax
    line="<tr>"
    # for c,d in zip(cumulative, rolling_mean_diff):
    for c,d in zip(cumulative, diff):
        rgb = matplotlib.colors.to_hex(cmap(d/rollingdiffmax))
        line+='<td bgcolor="%s">%d</td>' % (rgb, c)
    for label in labels:
        line+="<td>%s</td>" % label
    return line + "</tr>"
    
total_max_cum, digits = maxdata(ts_sorted)
cmap=plt.get_cmap("Wistia")
toHTMLRow(5370, digits, cmap, labels=["5370"])


# In[ ]:


def toHTMLRow(AGS, digits, cmap, labels, rolling_window_size=5):
    row = ts_sorted[ts.columns[2:]].loc[AGS].astype('int')
    # return row

    window=rolling_window_size
    rolling_mean_cum = row.rolling(window=window, center=True).mean()
    # return rolling_mean_cum

    # diff= pandas.DataFrame(rolling_mean_cum).diff(axis=0).fillna(0)[AGS].tolist()
    diff= pandas.DataFrame(rolling_mean_cum).diff(axis=0)[AGS].tolist()
    # return diff
    
    cumulative=row.tolist()
    # return diff, cumulative
    diffmax = numpy.nanmax(diff)
    # return diffmax
    line="<tr>"
    # for c,d in zip(cumulative, rolling_mean_diff):
    for c,d in zip(cumulative, diff):
        rgb = matplotlib.colors.to_hex(cmap(d/diffmax))
        line+='<td bgcolor="%s"><span>%d</span></td>' % (rgb, c)
    for label in labels:
        line+="<td>%s</td>" % label
    return line + "</tr>"
    
total_max_cum, digits = maxdata(ts_sorted)
cmap=plt.get_cmap("Wistia")
cmap.set_bad("white")
toHTMLRow(5370, digits, cmap, labels=["5370"])


# In[ ]:


PAGE="""

<!DOCTYPE html>
<html>
<head>
<STYLE>

table {
  border-collapse: collapse;
}
th, td {
  text-align:center;
  font-family: 'Roboto Condensed', sans-serif;
}


td span
{
  font-family: 'Teko', sans-serif;
  text-align:center;
}


th
{
  vertical-align: bottom;
  text-align: center;
}

th span
{
  -ms-writing-mode: tb-rl;
  -webkit-writing-mode: vertical-rl;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  white-space: nowrap;
  font-family: sans-serif;
}
</STYLE>
<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed|Teko&display=swap" rel="stylesheet">
</head>
<body>
"""

PAGE_END="""
</body>
</html>
"""


# In[ ]:


total_max_cum, digits = maxdata(ts_sorted)
cmap=plt.get_cmap("Wistia")
# cmap.set_under(), cmap.set_over() outside [0,1]
district_AGSs = [1001, 1002, 5370, 9377]
district_AGSs = ts_sorted.index.tolist()

page = PAGE + "<table><tr>\n"
for col in ts.columns[2:]:
    page += "<th><span>%s</span></th>" % col

cols = ["Kreis", "Population", "Bundesland", "center day" ]
for col in cols:
    page += "<th>%s</th>" % col
page +="</tr>"
for AGS in district_AGSs:
    gen, bez, inf, pop = AGS_to_population(AGS)
    name_BL, inf_BL, pop_BL = AGS_to_Bundesland(AGS)
    labels = ["%s (%s)" % (gen, bez)]
    labels += [pop]
    labels += [name_BL]
    labels += ["%.2f"% (ts_sorted["centerday"][AGS])]
    page += toHTMLRow(AGS, digits, cmap, labels) + "\n"
page += "</table>" + PAGE_END

fn=os.path.join(PAGES_PATH, "test.html")
with open(fn, "w") as f:
    f.write(page)
print (fn)

