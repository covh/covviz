'''
Created on 25 Apr 2020

@author: andreas
'''

import os, datetime

import pandas
import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling, dataPlotting, districtDistances



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

def Districts_to_HTML_table(ts_sorted, datacolumns, bnn, distances, district_AGSs, cmap, filename="kreise_Germany.html", km=50, rolling_window_size=5, header=PAGE, footer=PAGE_END):

    # total_max_cum, digits = maxdata(ts_sorted)
    
    page = header  + "<table><tr>\n"
    for col in datacolumns:
        page += "<th><span>%s</span></th>" % col
    
    cols = ["Kreis", "Population", "Bundesland", "center day" ] # , "<= %d km" % km]
    for col in cols:
        page += "<th>%s</th>" % col
    page +="</tr>"
    
    for AGS in district_AGSs:
        gen, bez, inf, pop = dataMangling.AGS_to_population(bnn, AGS)
        name_BL, inf_BL, pop_BL = dataMangling.AGS_to_Bundesland(bnn, AGS)
        # print (AGS)
        # nearby_links = districtDistances.kreis_nearby_links(bnn, distances, AGS, km) if AGS else ""
        labels = [districtDistances.kreis_link(bnn, AGS)[2]]
        labels += ['{:,}'.format(pop)]
        labels += [name_BL]
        labels += ["%.2f"% (ts_sorted["centerday"][AGS])]
        # labels += [nearby_links]
        page += toHTMLRow(ts_sorted, AGS, datacolumns, cmap, labels, rolling_window_size=rolling_window_size) + "\n"
        
    page += "</table>" + footer
    
    fn=None
    if filename:
        fn=os.path.join(dataFiles.PAGES_PATH, filename)
        with open(fn, "w") as f:
            f.write(page)
    
    return fn, page
    

def BuLas_to_HTML_table(Bundeslaender, datacolumns, names, cmap, table_filename="bundeslaender_Germany.html", rolling_window_size=3):

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
    
def colormap():
    cmap=plt.get_cmap("Wistia")
    cmap.set_bad("white")
    return cmap


if __name__ == '__main__':

    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled()
    
       
    AGS = 1001
    AGS = 5370
    print ( ts_sorted["centerday"][AGS] )

    cmap = colormap()  
    
    print ( toHTMLRow(ts_sorted, AGS, datacolumns, cmap, labels=["%s" % AGS]) ) 

    district_AGSs = [1001, 1002, 5370, 9377]
    # district_AGSs = ts_sorted.index.tolist()
    
    distances = districtDistances.load_distances()
    print (Districts_to_HTML_table(ts_sorted, datacolumns, bnn, distances, district_AGSs, cmap, km=50))
    
    # Bundeslaender.loc['Deutschland'] = Bundeslaender.sum().values.tolist()
    
    print (BuLas_to_HTML_table(Bundeslaender_sorted, datacolumns, Bundeslaender_sorted.index.tolist(), cmap))
