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


def footerlink():
    text = '<hr><a href="https://covh.github.io/cov19de">tiny.cc/cov19de</a>'
    dt = ("%s" % datetime.datetime.now())[:19]
    text +=" page generated %s." % dt
    return text

def bundesland(BL_name, filename_PNG, title, pop_BL, cumulative, filename_HTML, ts, ts_sorted, datacolumns, bnn, distances, cmap, km):
    page = dataTable.PAGE % BL_name

    district_AGSs = ts_sorted[ts_sorted.Bundesland==BL_name].index.tolist()
    
    page +='<a name="top">'
    page +='Up to <a href="about.html">about.html</a> or to overview of <a href="Deutschland.html">Germany</a>\n'
    page +='Or down to <a href="#Kreise">Kreise (districts)</a>'
    flagimg = dataTable.flag_image(BL_name, pop_BL, height=20)
    page +="<hr><h1>%s %s, and its %d districts (%s)</h1>\n" % (flagimg, BL_name, len(district_AGSs), datacolumns[-1])
    page +='<img src="%s"/><p/>' % ("../pics/" + filename_PNG)
    page += "population: {:,}".format(pop_BL)
    prevalence = 1000000.0 * cumulative[-1] / pop_BL 
    page += " --> current prevalence: %d known infected per 1 million population<br/>\n" % (prevalence )
    page +='total cases: <span style="color:#1E90FF; font-size:x-small;">%s</span><p/>\n' % (list(map(int, cumulative)))
    
    page +="<hr><h2 id='Kreise'>%s's %d Kreise</h2>\n" % (BL_name, len(district_AGSs))
    page +="<h3>Sorted by 'center day'</h3>\n"
    
    page +="Click on name of Kreis to see detailed data.<p/>\n"
    
    districtsHTML = dataTable.Districts_to_HTML_table(ts_sorted, datacolumns, bnn, 
                                                      district_AGSs, cmap, filename=None, 
                                                      rolling_window_size=5, header="\n", footer="\n")
    
    page+=districtsHTML[1]
    page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'

    for AGS in district_AGSs:
        gen, bez, inf, pop = dataMangling.AGS_to_population(bnn, AGS)
        daily, cumulative, title, filename = dataMangling.get_Kreis(ts, bnn, str(AGS))
        
        nearby_links = districtDistances.kreis_nearby_links(bnn, distances, AGS, km) if AGS else ""
        AGS_5digits = ("00000%s" % AGS) [-5:] 
        anchor = "AGS%s" % (AGS_5digits)
        page +="<hr><h3 id=%s>%s AGS=%s</h3>\n" % (anchor, title, AGS)
        # print (cumulative)
        page +="Neighbours within %d km: %s<p/>\n" % (km, nearby_links)
        filename_kreis_PNG = "Kreis_" + ("00000"+str(AGS))[-5:] + ".png"
        page +='<img src="%s"/><p/>' % ("../pics/" + filename_kreis_PNG)
        
        prevalence = cumulative[-1] / pop * 1000000
        page += ("%s %s" % (bez, gen)) + " population: {:,}".format(pop)
        page += " --> current prevalence: %d known infected per 1 million people.<br/>\n" % (prevalence )

        page +='total cases: <span style="color:#1E90FF; font-size:x-small;">%s</span><p/>\n' % (list(map(int, cumulative)))
        
        page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'
    
    page +=footerlink()
    page += dataTable.PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, filename_HTML)
    with open(fn, "w") as f:
        f.write(page)
    
    return fn

def Bundeslaender_alle(Bundeslaender, ts, ts_sorted, datacolumns, bnn, distances, cmap, km):
    print ("Creating HTML files for all 'Bundeslaender'")
    filenames, population = [], 0
    rootpath = os.path.abspath(dataFiles.REPO_PATH)
    
    for BL_name in Bundeslaender.index.tolist():
    # for BL_name in ["Dummyland"]:
        if BL_name == "Deutschland":
            continue
        print (BL_name, end=" ")
        daily, cumulative, title, filename_PNG, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL_name, datacolumns)
        filename_HTML = filename_PNG.replace(".png", ".html")
        filename_HTML = filename_HTML.replace("bundesland_", "")

        fn = bundesland(BL_name, filename_PNG, title, pop_BL, cumulative, filename_HTML, ts, ts_sorted, datacolumns, bnn, distances, cmap, km)
        fn_abs = os.path.abspath(fn).replace(rootpath, "")
        
        filenames.append((BL_name, fn_abs ))
        population += pop_BL
    print ("\nTotal population covered:", population)
    print ("%d filenames written: %s" % (len(filenames), filenames))
    
    return filenames
    
    
def Deutschland_simple(Bundeslaender_filenames, filename_HTML="Deutschland_simple.html"):
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
    
    
GOOGLESHEET_HTML="""

<hr><h3 id=googlesheet>401 Kreise - Ranked by MORTALITY</h3>
Note that the <b>old sorting by mortality</b> (how many deads per
1 million population) is now also linking every Kreis (district) to
this website here = so that is another way how the regions can be sorted. <br/>
Perhaps remember the --&gt; shortcut to
that googlesheet --&gt; <a href="http://tiny.cc/kreise">tiny.cc/kreise</a><p/>

(Screenshot below is not updated, so:) Click on the image to see a more recent <b>mortality sorting</b>.<p/> 
<table border="0" cellspacing="2" cellpadding="2">
<tbody>
<tr>
<td>
<a href="https://docs.google.com/spreadsheets/d/1KbNjq2OPsSRzmyDDidbXD4pcPnAPfY0SsS693duadLw/#gid=1644486167">
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="../pics/googlesheet-mortality-top-20200430.png"
     alt="table of Kreise sorted by mortality" border="0" width="100%" />
</a><br>
</td></tr>
</tbody>
</table>
<br>
"""
# width="583" height="320"

def fourbyfour(Bundeslaender_sorted, ifPrint=False):
    
    print ("\ngenerating 4x4 html table, for overview of 16 Bundeslaender in Germany:")
    BLs=sorted(Bundeslaender_sorted.index.tolist())
    BLs = [BL for BL in BLs if BL not in ("Dummyland", "Deutschland")]
    
    global page
    page=""
    c=0
    
    class page(object):
        page=""
        def a(self, t):
            self.page+=t+"\n"
           
    p=page()
    p.a("<table>")
    for i in range(4):
        p.a("<tr>")
        for j in range(4):
            print(c, BLs[c])
            imgprop='src="https://covh.github.io/cov19de/pics/bundesland_%s.png" alt="bundesland_%s.png"'%(BLs[c],BLs[c])
            p.a('<td><a href="%s.html">%s<br/><img %s width="366" height="214"></a></td>' % (BLs[c], BLs[c], imgprop))
            c+=1
        p.a("</tr>")
    p.a("</table>")
    if ifPrint:
        print (p.page)
    return p.page


def Deutschland(Bundeslaender_sorted, datacolumns, cmap, ts_sorted, bnn, filename_HTML="Deutschland.html"):
    page = dataTable.PAGE % "Deutschland"
    page +='<a name="top">'
    page +='UP to <a href="about.html">about.html</a> \n'
    page +='| or DOWN to <a href="#Bundeslaender">16 Bundesländer</a>, or Bundesländer plots <a href="#Bundeslaender_4by4">alphabetically</a> or <a href="#Kreise">401 Kreise</a> '
    page +='or 401 Kreise sorted by <a href="#googlesheet">mortality</a> (googlesheet table).'
    
    page +='<hr><h1 id="de">Germany</h1>\n' 
    page +='<img src="%s"/><p/>' % ("../pics/Deutschland.png")
    
    DE=Bundeslaender_sorted.drop(["Deutschland", "Dummyland"]).sum()
    cumulative = DE[datacolumns].astype(int).tolist()
    
    prevalence = cumulative[-1] / DE["Population"] * 1000000
    page += "population: {:,}".format(DE["Population"])
    page += " --> current prevalence: %d known infected per 1 million population<br/>\n" % (prevalence )
    
    page +='total cases: <span style="color:#1E90FF; font-size:x-small;">%s</span><p/>\n' % (list(map(int, cumulative)))

    
    page +='<hr><h2 id="Bundeslaender">16 Bundesländer</h2>\n'
    page +='<h3 id="Bundeslaender_centerday">ranked by "center day"</h3>\n'
    page +="Click on Bundesland name to see detailed data.<p/>\n"
    
    BL_names = Bundeslaender_sorted.index.tolist()
    fn, bulaHTML= dataTable.BuLas_to_HTML_table(Bundeslaender_sorted, datacolumns, BL_names, cmap, table_filename=None, rolling_window_size=3, header="\n", footer="\n")
    
    page+=bulaHTML
    
    page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'
    
    page +='<hr><h3 id="Bundeslaender_4by4">alphabetically</h3>\n'
    
    page += '<div class="fourbyfour">' # give it scrollbars so that it's not crazy wide on mobile
    page += fourbyfour(Bundeslaender_sorted)
    page += '</div>'
    
    page +="<p>Click on the image of a Bundesland to enter its page, with all its districts.</p>"
    page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'
    
    
    page +='<hr><h2 id="Kreise">401 Kreise (districts)</h2>\n'
    page +='<h3>ranked by "center day" or other measures ...</h3>\n'
    page +='<a href="#">Back to top</a><p/>\n'
    
    page +="Click on name of Kreis (or Bundesland) to see detailed data. Click on a table header to sort by that column.\n"
    
    district_AGSs = ts_sorted.index.tolist()
    fn, kreiseHTML = dataTable.Districts_to_HTML_table(ts_sorted, datacolumns, bnn, district_AGSs, cmap, filename="kreise_Germany.html", header="\n", footer="\n")
    page += kreiseHTML 
    
    page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'
    
    page +=GOOGLESHEET_HTML
    page +='<a href="#">Back to top</a> or: Up to <a href="about.html">about.html</a>\n'

    
    page +=footerlink()
    
    page += dataTable.PAGE_END
    
    fn=os.path.join(dataFiles.PAGES_PATH, filename_HTML)
    with open(fn, "w") as f:
        f.write(page)
    
    return os.path.abspath(fn)



if __name__ == '__main__':
    
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled()
    # fourbyfour(Bundeslaender_sorted); exit()
    
    distances = districtDistances.load_distances()
    print()
    print()
    cmap = dataTable.colormap()
    # print ( bundesland("Hessen", "bundesland_Hessen.png", "Hessen", 7777, [8,9,10], "Hessen.html", ts, ts_sorted, datacolumns, bnn, distances, cmap, 50) ); exit()
    
    Bundeslaender_filenames = Bundeslaender_alle(Bundeslaender_sorted, ts, ts_sorted, datacolumns, bnn, distances, cmap, km=50); print (Bundeslaender_filenames)
    # Bundeslaender_filenames = [('Brandenburg', '../data/../pages/Brandenburg.html'), ('Bremen', '../data/../pages/Bremen.html'), ('Thüringen', '../data/../pages/Thüringen.html'), ('Bayern', '../data/../pages/Bayern.html'), ('Saarland', '../data/../pages/Saarland.html'), ('Hessen', '../data/../pages/Hessen.html'), ('Schleswig-Holstein', '../data/../pages/Schleswig-Holstein.html'), ('Baden-Württemberg', '../data/../pages/Baden-Württemberg.html'), ('Niedersachsen', '../data/../pages/Niedersachsen.html'), ('Sachsen-Anhalt', '../data/../pages/Sachsen-Anhalt.html'), ('Sachsen', '../data/../pages/Sachsen.html'), ('Hamburg', '../data/../pages/Hamburg.html'), ('Berlin', '../data/../pages/Berlin.html'), ('Rheinland-Pfalz', '../data/../pages/Rheinland-Pfalz.html'), ('Nordrhein-Westfalen', '../data/../pages/Nordrhein-Westfalen.html'), ('Mecklenburg-Vorpommern', '../data/../pages/Mecklenburg-Vorpommern.html'), ('Dummyland', '../data/../pages/Dummyland.html')]
    # Deutschland_simple(Bundeslaender_filenames)
    
    fn=Deutschland(Bundeslaender_sorted, datacolumns, cmap, ts_sorted, bnn )
    print ("\n" + fn)
    
    
