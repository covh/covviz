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



def toHTMLRow(ts_sorted, row_index, datacolumns, cmap, labels, rolling_window_size=7):
    row = ts_sorted[datacolumns].loc[row_index].astype('int')
    # return row

    window=rolling_window_size
    rolling_mean_cum = row.rolling(window=window, center=True).mean()

    diff_rolling_mean = pandas.DataFrame(rolling_mean_cum).diff(axis=0).clip(lower=0)[row_index].tolist()
    diffmax = numpy.nanmax(diff_rolling_mean)
    
    cumulative=row.tolist()
    line="<tr>"
    for c, d in zip(cumulative, diff_rolling_mean):
        #                                    avoid extreme colors, shifted towards red: 0.30-0.80
        rgb = matplotlib.colors.to_hex(cmap( 0.30+(d/diffmax)*0.50 ))
        
        line+='<td bgcolor="%s"><span>%d</span></td>' % (rgb, c)
    for label in labels:
        line+="<td>%s</td>" % label
    return line + "</tr>"
    


PAGE="""

<!DOCTYPE html>
<html>
<head>
<TITLE>%s</TITLE>
<STYLE>

table {
  border-collapse: collapse;
}

body {
  font-family: 'Roboto', sans-serif;
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
  vertical-align: middle;
  text-align: center;
  border: 1px solid black;
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

.flag 
{
    border:1px solid #777777;
}

.tablearea {
    overflow-y: scroll;
    overflow-x: scroll;
    width: 100%%;
    max-height: 670px;
    display: inline-block;
}

.fourbyfour {
    overflow-y: scroll;
    overflow-x: scroll;
    width: 100%%;
    height: 1000px;
}




</STYLE>
<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed|Teko&display=swap" rel="stylesheet">

</head>
<body onload="scroll_rightmost()">
"""

# It is a best practice to put JavaScript <script> tags 
# just before the closing </body> tag 
# rather than in the <head> section of your HTML. 
# The reason for this is that HTML loads from top to bottom. 
# The head loads first, then the body, and then everything inside the body.
 
PAGE_END="""
<script type="text/javascript" src="sort-table.js"></script>
<script type="text/javascript" src="scroller.js"></script>
</body>
</html>
"""

def flag_image(name, population=None, height=14):
    fn = "../pics/flag_%s.svg" % name
    info_str = name
    info_str  += " population={:,}".format(population) if population else ""
    text = '<img class="flag" height=%d src="%s" alt="%s" title="%s"/>' % (height, fn, fn, info_str)
    return text


def prevalence(datatable, row_index, datacolumns, population):
    cumulative = datatable[datacolumns].loc[row_index].astype('int')
    prev1mio = cumulative[-1] / population * 1000000
    return prev1mio

def bulaLink(name):
    return '<a href="%s.html">%s</a>' % (name, name)


ATTRIBUTION = """<span style="color:#aaaaaa; font-size:x-small;">Source data from "Risklayer GmbH (www.risklayer.com) and Center for Disaster Management and Risk Reduction Technology (CEDIM) at Karlsruhe Institute of Technology (KIT) and the Risklayer-CEDIM SARS-CoV-2 Crowdsourcing Contributors". Data sources can be found under https://docs.google.com/spreadsheets/d/1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s/edit?usp=sharing Authors: James Daniell| Johannes Brand| Andreas Schaefer and the Risklayer-CEDIM SARS-CoV-2 Crowdsourcing Contributors through Risklayer GmbH and Center for Disaster Management and Risk Reduction Technology (CEDIM) at the Karlsruhe Institute of Technology (KIT).</span><p/>""" 


def Districts_to_HTML_table(ts_sorted, datacolumns, bnn, district_AGSs, cmap, filename="kreise_Germany.html", rolling_window_size=3, header=PAGE % "Deutschland Kreise", footer=PAGE_END, divEnveloped=True):

    # total_max_cum, digits = maxdata(ts_sorted)
    
    tid="table_districts"
    page = header 
    if divEnveloped:
        page+= '<div class="tablearea" id="tablediv_kreise">'
    page+= '<table id="%s">\n' % tid
    caption="Click on column header name, to sort by that column; click again for other direction."
    page += '<caption id="caption_kreise" style="text-align:right;">%s</caption>\n' % caption
    page +="<tr>"
    
    for col in datacolumns:
        page += "<th><span>%s</span></th>" % col
    
    colcount=len(datacolumns)
    # print (datacolumns, colcount); exit()
    cols = [("7days new cases", True),
            ("Kreis", True),
            ("Prev. p.1mio", True),
            ("7days Incid.p.1mio", True),
            # ("7days Incid.p.1mio", True),
            ("Population", True),
            ("center day", True),
            ("Reff_4_7", True),
            ("Bundesland", True),
            ("info", False) ] 
    
    for i, col in enumerate(cols):
        colName, sorting = col
        if sorting:
            cellid = "\'%shc%d\'" % (tid, i + colcount)
            page += '<th onclick="sortTable(\'%s\', %d, %s)" id=%s>%s</th>' % (tid, i + colcount, cellid, cellid, colName)
        else:
            page += '<th>%s</th>' % (colName)
            
    page +="</tr>"
    
    for AGS in district_AGSs:
        gen, bez, inf, pop = dataMangling.AGS_to_population(bnn, AGS)
        name_BL, inf_BL, pop_BL = dataMangling.AGS_to_Bundesland(bnn, AGS)
        # print (AGS)
        # nearby_links = districtDistances.kreis_nearby_links(bnn, distances, AGS, km) if AGS else ""
        labels=[]
        labels += ['%d' % (ts_sorted["new_last7days"][AGS])]
        labels += [districtDistances.kreis_link(bnn, AGS)[2]]
        labels += ["%d" % prevalence(datatable=ts_sorted, row_index=AGS, datacolumns=datacolumns, population=pop)]
        labels += ['%d' % (1000000*ts_sorted["new_last7days"][AGS] / pop)]
        # labels += ['%d' % (1000000*ts_sorted["new_last7days"][AGS] / pop)]
        labels += ['{:,}'.format(pop)]
        labels += ["%.1f"% (ts_sorted["centerday"][AGS])]
        labels += ["%.2f"% (ts_sorted["Reff_4_7_last"][AGS])]
        labels += [bulaLink(name_BL)]
        labels += [flag_image(name_BL, pop_BL)]
        # labels += [nearby_links]
        page += toHTMLRow(ts_sorted, AGS, datacolumns, cmap, labels, rolling_window_size=rolling_window_size) + "\n"
        
    page += "</table>"
    if divEnveloped:
        page += "</div>" 
    page += ATTRIBUTION + footer
    
    fn=None
    if filename:
        fn=os.path.join(dataFiles.PAGES_PATH, filename)
        with open(fn, "w") as f:
            f.write(page)
    
    return fn, page
    

def BuLas_to_HTML_table(Bundeslaender, datacolumns, BL_names, cmap, table_filename="bundeslaender_Germany.html", rolling_window_size=3, header = PAGE % "Bundeslaender", footer=PAGE_END, divEnveloped=True):

    # total_max_cum, digits = maxdata(ts_sorted)
    
    tid="table_bundeslaender"
    page = header
    if divEnveloped:
        page += '<div class="tablearea" id="tablediv_bundeslaender">' 
    page += '<table id="%s">\n' % tid
    caption="Click on column header name, to sort by that column; click again for other direction."
    page += '<caption style="text-align:right;">%s</caption>' % caption
    page +="<tr>"

    for col in datacolumns:
        page += "<th><span>%s</span></th>" % col
    colcount=len(datacolumns)
       
    cols = ["7days new cases", "Bundesland", "info", "Prev. p.1mio", "7days Incid.p.1mio", "Population", "center day", "Reff_4_7" ]
    
    for i, colName in enumerate(cols):
        cellid = "\'%shc%d\'" % (tid, i + colcount)
        page += '<th onclick="sortTable(\'%s\', %d, %s)" id=%s>%s</th>' % (tid, i + colcount, cellid, cellid, colName)
    page +="</tr>"
    
    for name_BL in BL_names:
        labels=[]
        daily, cumulative, title, filename, pop_BL = dataMangling.get_BuLa(Bundeslaender, name_BL, datacolumns)
        labels += ['%d' % (Bundeslaender["new_last7days"][name_BL])]
        labels += [bulaLink(name_BL)]
        labels += [flag_image(name_BL)]
        labels += ["%d" % prevalence(datatable=Bundeslaender, row_index=name_BL, datacolumns=datacolumns, population=pop_BL)]
        labels += ['%d' % (1000000*Bundeslaender["new_last7days"][name_BL] / pop_BL)]
        labels += ['{:,}'.format(pop_BL)]
        labels += ["%.2f"% (Bundeslaender["centerday"][name_BL])]
        labels += ["%.2f"% (Bundeslaender["Reff_4_7_last"][name_BL])]
        page += toHTMLRow(Bundeslaender, name_BL, datacolumns, cmap, labels, rolling_window_size=rolling_window_size) + "\n"
        
    page += "</table>"
    if divEnveloped:
        page +=" </div>" 
    page += ATTRIBUTION + footer
    
    fn=None
    if table_filename:
        fn=os.path.join(dataFiles.PAGES_PATH, table_filename)
        with open(fn, "w") as f:
            f.write(page)

    return fn, page
    
def colormap():
    # cmap=plt.get_cmap("Wistia")
    # cmap=plt.get_cmap("summer")
    
    """
    # too dark:
    import matplotlib.colors as mcolors
    cdict = {'red':   ((0.0, 0.0, 0.0),
                       (0.5, 0.0, 0.0),
                       (1.0, 1.0, 1.0)),
             'blue':  ((0.0, 0.0, 0.0),
                       (1.0, 0.0, 0.0)),
             'green': ((0.0, 0.0, 1.0),
                       (0.5, 0.0, 0.0),
                       (1.0, 0.0, 0.0))}
    cmap = mcolors.LinearSegmentedColormap('my_colormap', cdict, 100)
    """
    # cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","yellow","red"])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","yellow","red"])
    
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
    district_AGSs = ts_sorted.index.tolist()
    
    distances = districtDistances.load_distances()
    print (Districts_to_HTML_table(ts_sorted, datacolumns, bnn, district_AGSs, cmap, divEnveloped=False)[0])
    
    # Bundeslaender.loc['Deutschland'] = Bundeslaender.sum().values.tolist()
    
    print (BuLas_to_HTML_table(Bundeslaender_sorted, datacolumns, Bundeslaender_sorted.index.tolist(), cmap, divEnveloped=False)[0])
