'''
Created on 25 Apr 2020

@author: andreas
'''

import os, datetime

import pandas
import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling, dataPlotting


def add_centerday_column(ts, ts_BuLa):
    
    ts_BuLa["centerday"] = [ dataMangling.temporal_center( dataMangling.AGS_to_ts_daily(ts, "%s" % AGS) )[0]
                            for AGS in ts_BuLa["AGS"].tolist() ]
    ts_sorted = ts_BuLa.sort_values("centerday").set_index("AGS")

    return ts_sorted


def add_centerday_column_Bundeslaender(Bundeslaender):
    Bundeslaender["centerday"] = [dataMangling.temporal_center(dataMangling.get_BuLa(Bundeslaender, name)[0])[0]
                                  for name in Bundeslaender.index.tolist() ]
    Bundeslaender.sort_values("centerday",inplace=True)
    return Bundeslaender


def maxdata(ts_sorted):
    maxvalue = max(ts_sorted[ts.columns[2:]].max())
    digits=int(1+numpy.log10(maxvalue))
    return maxvalue, digits


def toHTMLRow(ts_sorted, row_index, datacolumns, cmap, labels, rolling_window_size=5):
    row = ts_sorted[datacolumns].loc[row_index].astype('int')
    # return row

    window=rolling_window_size
    rolling_mean_cum = row.rolling(window=window, center=True).mean()
    # return rolling_mean_cum

    # diff= pandas.DataFrame(rolling_mean_cum).diff(axis=0).fillna(0)[AGS].tolist()
    diff= pandas.DataFrame(rolling_mean_cum).diff(axis=0)[row_index].tolist()
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

def Districts_to_HTML_table(ts_sorted, datacolumns, bnn, district_AGSs, cmap, filename="kreise_Germany.html", rolling_window_size=5):

    # total_max_cum, digits = maxdata(ts_sorted)
    
    page = PAGE + "<table><tr>\n"
    for col in datacolumns:
        page += "<th><span>%s</span></th>" % col
    
    cols = ["Kreis", "Population", "Bundesland", "center day" ]
    for col in cols:
        page += "<th>%s</th>" % col
    page +="</tr>"
    
    for AGS in district_AGSs:
        gen, bez, inf, pop = dataMangling.AGS_to_population(bnn, AGS)
        name_BL, inf_BL, pop_BL = dataMangling.AGS_to_Bundesland(bnn, AGS)
        labels = ["%s (%s)" % (gen, bez)]
        labels += ['{:,}'.format(pop)]
        labels += [name_BL]
        labels += ["%.2f"% (ts_sorted["centerday"][AGS])]
        page += toHTMLRow(ts_sorted, AGS, datacolumns, cmap, labels, rolling_window_size=rolling_window_size) + "\n"
        
    page += "</table>" + PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, filename)
    with open(fn, "w") as f:
        f.write(page)
    return fn
    

def BuLas_to_HTML_table(Bundeslaender_sorted, datacolumns, names, cmap, table_filename="bundeslaender_Germany.html", rolling_window_size=3):

    # total_max_cum, digits = maxdata(ts_sorted)
    
    page = PAGE + "<table><tr>\n"
    for col in datacolumns:
        page += "<th><span>%s</span></th>" % col
    
    cols = ["Bundesland", "Population", "center day" ]
    for col in cols:
        page += "<th>%s</th>" % col
    page +="</tr>"
    
    for BL in names:
        daily, cumulative, title, filename, pop = dataMangling.get_BuLa(Bundeslaender, BL)
        labels = ["%s" % BL]
        labels += ['{:,}'.format(pop)]
        labels += ["%.2f"% (Bundeslaender["centerday"][BL])]
        page += toHTMLRow(Bundeslaender, BL, datacolumns, cmap, labels, rolling_window_size=rolling_window_size) + "\n"
        
    page += "</table>" + PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, table_filename)
    with open(fn, "w") as f:
        f.write(page)
    return fn
    


if __name__ == '__main__':

    ts, bnn = dataFiles.data(withSynthetic=True)
    dates = dataMangling.dates_list(ts)
    datacolumns = ts.columns[2:]
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
   
    ts_sorted = add_centerday_column(ts, ts_BuLa)
    # print ( maxdata(ts_sorted) )
    
    AGS = 1001
    AGS = 5370
    print ( ts_sorted["centerday"][AGS] )

    # total_max_cum, digits = maxdata(ts_sorted)
    cmap=plt.get_cmap("Wistia")
    cmap.set_bad("white")
    
    print ( toHTMLRow(ts_sorted, AGS, datacolumns, cmap, labels=["%s" % AGS]) ) 

    district_AGSs = [1001, 1002, 5370, 9377]
    district_AGSs = ts_sorted.index.tolist()
    
    print (Districts_to_HTML_table(ts_sorted, datacolumns, bnn, district_AGSs, cmap))
    
    # Bundeslaender.loc['Deutschland'] = Bundeslaender.sum().values.tolist()
    Bundeslaender_sorted = add_centerday_column_Bundeslaender(Bundeslaender)
    print (BuLas_to_HTML_table(Bundeslaender_sorted, datacolumns, Bundeslaender.index.tolist(), cmap))
