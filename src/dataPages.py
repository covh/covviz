'''
Created on 27 Apr 2020

@author: andreas
'''

import os, datetime

import pandas
import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling, dataPlotting, districtDistances, dataTable

def bundesland(BL_name, filename_PNG, title, cumulative, filename_HTML, ts_sorted, datacolumns, bnn, distances, cmap, km):
    page = dataTable.PAGE
    
    page +='<a name="#top">'
    page +="<h1>%s</h1>\n" % title
    page +='<img src="%s"/><p/>' % ("../pics/" + filename_PNG)
    page +="total cases: %s<p/>\n" % cumulative
    
    district_AGSs = ts_sorted[ts_sorted.Bundesland==BL_name].index.tolist()
    page +="<h2>%d Kreise</h2>\n" % len(district_AGSs)
    
    districtsHTML = dataTable.Districts_to_HTML_table(ts_sorted, datacolumns, bnn, distances, 
                                                      district_AGSs, cmap, filename=None, 
                                                      km=50, rolling_window_size=5, header="\n", footer="\n")
    page+=districtsHTML[1]

    for AGS in district_AGSs:
        gen, bez, inf, pop = dataMangling.AGS_to_population(bnn, AGS)
        daily, cumulative, title, filename = dataMangling.get_Kreis(ts, bnn, str(AGS))
        nearby_links = districtDistances.kreis_nearby_links(bnn, distances, AGS, km) if AGS else ""
        AGS_5digits = ("00000%s" % AGS) [-5:] 
        anchor = "AGS%s" % (AGS_5digits)
        page +="<h3 id=%s>%s AGS=%s</h3>\n" % (anchor, title, AGS)
        # print (cumulative)
        page +="Neighbours within %d km: %s<p/>\n" % (km, nearby_links)
        filename_kreis_PNG = "Kreis_" + ("00000"+str(AGS))[-5:] + ".png"
        page +='<img src="%s"/><p/>' % ("../pics/" + filename_kreis_PNG)
        page +="Total cases: %s<p/>\n" % (list(map(int, cumulative)))
        page +='<a href="#top">Back to top</a>\n'
    
    page += dataTable.PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, filename_HTML)
    with open(fn, "w") as f:
        f.write(page)
    
    return fn

def Bundeslaender_all(Bundeslaender):
    filenames, population = [], 0
    for BL in Bundeslaender.index.tolist():
        print (BL, end=" ")
        daily, cumulative, title, filename_PNG, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL)
        filename_HTML = filename_PNG.replace(".png", ".html")
        filename_HTML = filename_HTML.replace("bundesland_", "")

        bundesland(BL, filename_PNG, title, cumulative, filename_HTML)
        filenames.append(filename_HTML)
        population += pop_BL
    print ("\nTotal population covered:", population)
    print ("%d filenames written: %s" % (len(filenames), filenames))

if __name__ == '__main__':
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled()
    distances = districtDistances.load_distances()
    print()
    print()
    cmap = dataTable.colormap()
    print ( bundesland("Hessen", "bundesland_Hessen.png", "Hessen Population=6265809", [8,9,10], "Hessen.html", ts_sorted, datacolumns, bnn, distances, cmap, 50) ) 
    exit()
    
    Bundeslaender_all(Bundeslaender_sorted)
