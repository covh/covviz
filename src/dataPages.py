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

def bundesland(BL_name, filename_PNG, title, pop_BL, cumulative, filename_HTML, ts_sorted, datacolumns, bnn, distances, cmap, km):
    page = dataTable.PAGE

    district_AGSs = ts_sorted[ts_sorted.Bundesland==BL_name].index.tolist()
    
    page +='<a name="#top">'
    page +='Up to <a href="about.html">about.html</a>\n'
    page +="<h1>%s, and its %d districts (%s)</h1>\n" % (BL_name, len(district_AGSs), datacolumns[-1])
    page +='<img src="%s"/><p/>' % ("../pics/" + filename_PNG)
    page +="total cases: %s<br>\n" % (list(map(int, cumulative)))
    prevalence = cumulative[-1] / pop_BL * 1000000
    page += "population: {:,}".format(pop_BL)
    page += " --> current prevalence: %d known infected per 1 million population<p/>\n" % (prevalence )
    
    page +="<h2>%s's %d Kreise</h2>\n" % (BL_name, len(district_AGSs))
    page +="<h3>Sorted by 'center day'</h3>\n"
    
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
        page +="Total cases: %s<br>\n" % (list(map(int, cumulative)))
        
        prevalence = cumulative[-1] / pop * 1000000
        page += ("%s %s" % (bez, gen)) + " population: {:,}".format(pop)
        page += " --> current prevalence: %d known infected per 1 million people.<p/>\n" % (prevalence )
        
        page +='<a href="#top">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'
    
    page += dataTable.PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, filename_HTML)
    with open(fn, "w") as f:
        f.write(page)
    
    return fn

def Bundeslaender_alle(Bundeslaender, ts_sorted, datacolumns, bnn, distances, cmap, km):
    print ("Creating HTML files for all 'Bundeslaender'")
    filenames, population = [], 0
    for BL_name in Bundeslaender.index.tolist():
        if BL_name == "Deutschland":
            continue
        print (BL_name, end=" ")
        daily, cumulative, title, filename_PNG, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL_name)
        filename_HTML = filename_PNG.replace(".png", ".html")
        filename_HTML = filename_HTML.replace("bundesland_", "")

        fn = bundesland(BL_name, filename_PNG, title, pop_BL, cumulative, filename_HTML, ts_sorted, datacolumns, bnn, distances, cmap, km)
        filenames.append((BL_name, fn ))
        population += pop_BL
    print ("\nTotal population covered:", population)
    print ("%d filenames written: %s" % (len(filenames), filenames))
    
    return filenames
    

def Deutschland(Bundeslaender_filenames, filename_HTML="Deutschland.html"):
    page = dataTable.PAGE
    page +='<a name="#top">'
    page +='Up to <a href="about.html">about.html</a>\n'
    
    page +="<h1>Germany and its 17 countries</h1>\n" 
    page +='<img src="%s"/><p/>' % ("../pics/Deutschland.png")
    page +="total cases: %s<br>\n" #  % (list(map(int, cumulative)))
    # prevalence = cumulative[-1] / pop_BL * 1000000
    # page += "population: {:,}".format(pop_BL)
    # page += " --> current prevalence: %d known infected per 1 million population<p/>\n" % (prevalence )
    
    page +="<h2>16 Bundesländer</h2>\n"
    
    page +="<ul>\n"
    for BL_name, BL_filename in Bundeslaender_filenames:
        print(BL_name, BL_filename)
        page += '<li><a href="%s">%s</a></li>\n' % (BL_filename,BL_name)
    
    page +="</ul>\n"
        
    page +="<p/>TODO: Insert long 401 districts table"
    fn=os.path.join(dataFiles.PAGES_PATH, filename_HTML)
    with open(fn, "w") as f:
        f.write(page)
    
    return fn

if __name__ == '__main__':
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled()
    distances = districtDistances.load_distances()
    print()
    print()
    cmap = dataTable.colormap()
    # print ( bundesland("Hessen", "bundesland_Hessen.png", "Hessen", 7777, [8,9,10], "Hessen.html", ts_sorted, datacolumns, bnn, distances, cmap, 50) ); exit()
    
    Bundeslaender_filenames = Bundeslaender_alle(Bundeslaender_sorted, ts_sorted, datacolumns, bnn, distances, cmap, km=50)
    print (Bundeslaender_filenames)
    # Bundeslaender_filenames = [('Brandenburg', '../data/../pages/Brandenburg.html'), ('Bremen', '../data/../pages/Bremen.html'), ('Thüringen', '../data/../pages/Thüringen.html'), ('Bayern', '../data/../pages/Bayern.html'), ('Saarland', '../data/../pages/Saarland.html'), ('Hessen', '../data/../pages/Hessen.html'), ('Schleswig-Holstein', '../data/../pages/Schleswig-Holstein.html'), ('Baden-Württemberg', '../data/../pages/Baden-Württemberg.html'), ('Niedersachsen', '../data/../pages/Niedersachsen.html'), ('Sachsen-Anhalt', '../data/../pages/Sachsen-Anhalt.html'), ('Sachsen', '../data/../pages/Sachsen.html'), ('Hamburg', '../data/../pages/Hamburg.html'), ('Berlin', '../data/../pages/Berlin.html'), ('Rheinland-Pfalz', '../data/../pages/Rheinland-Pfalz.html'), ('Nordrhein-Westfalen', '../data/../pages/Nordrhein-Westfalen.html'), ('Mecklenburg-Vorpommern', '../data/../pages/Mecklenburg-Vorpommern.html'), ('Dummyland', '../data/../pages/Dummyland.html')]

    Deutschland(Bundeslaender_filenames)
    
    
