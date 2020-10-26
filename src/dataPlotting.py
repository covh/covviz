#!/usr/bin/env python3
"""
@summary: plot timeseries of (cumulative, daily) number of confirmed cases

@version: v03.4 (24/June/2020)
@since:   25/April/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@status:  Needs: (cleanup, function comments, etc.)
          See: todo.md for ideas what else to do. 
          NOT yet: pretty. But it works.
"""

import os, datetime

import pandas
# import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling


def plot_timeseries(dm: dataMangling.DataMangled, daily, cumulative, title, filename, ifShow=True, ifCleanup=True, population=None, limitIncidencePerWeekPerMillion=500):

    dates = dm.dates
    fig, ax = plt.subplots(figsize=(10, 6)) #, constrained_layout=True)
    # plt.tight_layout()

    # x axis
    ax.xaxis_date()
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
    fig.autofmt_xdate(rotation=60)

    # plot data
    lns1 = ax.plot(dates, daily, label="daily cases (weekend-flawed), 2 weeks: red", color='lightgray')
    lns1_2 = ax.plot(dates[-14:], daily[-14:], label="daily cases, last 14 days dark gray", color='red')
    # print (len(dates[-14:]))
    
    plt.ylabel("daily cases", color="purple")
    plt.ylim(0, max(daily[1:])*1.5)

    # plot averages
    window=7
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()   # FIXME: calculate outside of function
    lns2 = ax.plot(dates, rolling_mean, label='daily: centered moving average %s days' % window, color='purple')
    window=14
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()   # FIXME: calculate outside of function
    lns3 = ax.plot(dates, rolling_mean, label='daily: centered moving average %s days' % window, color='orange', linewidth=4)
    # window=21
    # rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    # ax.plot(dates, rolling_mean, label='SMA %s days' % window, color='pink', linewidth=1)

    # plot center bar
    center, signal = dataMangling.temporal_center(daily)
    # print (center)
    center_date = dm.datacolumns.values[int(round(center))]
    # lns4 = ax.bar(dates, signal, label="'expectation day': "+center_date, color='green')
    
    # lns4_2 = plt.plot(dates[int(round(center))], max(signal), marker="v", color='green', markersize=15)
    # lns4_2 = plt.plot(dates[int(round(center))], 0, marker="v", color='green', markersize=15)
    # lns4_2 = plt.plot(dates[int(round(center))], [max(daily[1:])/20], marker="^", color='green', markersize=30)
    lns4_2 = plt.plot(dates[int(round(center))], [max(daily[1:])/19], marker="v", color='green', markersize=17)


    # plot 2nd axis and cumulative data
    ax2 = plt.twinx()
    plt.ylim(0, max(cumulative)*1.1)
    
    plt.ylabel("cumulative total cases", color="#1E90FF")

    lns5 = ax2.plot(dates, cumulative, label="total cases reported at RiskLayer", color = '#1E90FF')
    
    lns6 = []
    if population:
        limit = limitIncidencePerWeekPerMillion/7*population/1000000
        # print ("limit:", limit)
        lns6 = ax.plot([dates[1]]+[dates[-1]],[limit,limit], label="daily %.2f =limit 500/week/1mio pop." % limit, color = '#ef7c7c', linestyle=  (0, (5, 10)))

    lines = lns5 + lns1 + lns2 + lns3 + lns6
    labs = [l.get_label() for l in lines]

    text = "source data @RiskLayer up to " + ("%s"%max(dates))[:10]
    text += "\nplot @DrAndreasKruger " + ("%s" % datetime.datetime.now())[:16]
    text += "\ndaily: (GREEN) 'expectation day' = "+center_date

    plt.legend(lines, labs, loc='upper left', facecolor="#fafafa", framealpha=0.8, 
               title=text, prop={'size': 8}, title_fontsize = 8)

    plt.title(title)
    
    if filename:
        fig.savefig(os.path.join(dataFiles.PICS_PATH, filename),  bbox_inches='tight')
    
    if ifShow:
        plt.show()
        
    if ifCleanup:
        plt.clf()
        plt.close("all")
    
    return plt, fig, ax, ax2


def test_plot_Kreis(dm):
    ## Kreis
    AGS = "0"
    #AGS = "1001"
    AGS = "5370"
    # AGS = "9377"
    dstr = dataMangling.get_Kreis(dm, AGS)
    plot_timeseries(dm, dstr.daily, dstr.cumulative, dstr.title, filename=dstr.filename, population=dstr.pop)


def plot_Kreise(dm, Kreise_AGS, ifPrint=True):
    done = []
    for AGS in Kreise_AGS:
        dstr = dataMangling.get_Kreis(dm, AGS)
        plot_timeseries(dm, dstr.daily, dstr.cumulative, dstr.title, filename=dstr.filename, ifShow=False, population=dstr.pop)
        done.append((dstr.title, dstr.filename))
        if ifPrint:
            print (dstr.title, dstr.filename)
        else:
            print (".", end="")
            if len(done)%60 == 0:
                print()
    if not ifPrint:
        print()
    return done


def test_plot_Bundesland(dm: dataMangling.DataMangled, Bundesland = "Hessen"):
    ## Bundesland
    # Bundesland = "Dummyland"
    
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(dm.ts, dm.bnn)
    daily, cumulative, title, filename, population = dataMangling.get_BuLa(Bundeslaender, Bundesland, dm.datacolumns)
    plot_timeseries(dm, daily, cumulative, title, filename=filename)


def plot_all_Bundeslaender(dm: dataMangling.DataMangled, ifPrint=True):
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(dm.ts, dm.bnn)
    filenames, population = [], 0
    done=[]
    for BL in Bundeslaender.index.tolist():
        print (BL, end=" ")
        daily, cumulative, title, filename, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL, dm.datacolumns)
        if BL=="Deutschland":
            filename = filename.replace("bundesland_", "")
        plot_timeseries(dm, daily, cumulative, title, filename=filename, ifShow=False)
        filenames.append(filename)
        population += pop_BL
        if ifPrint:
            print (title, filename)
        done.append((title, filename))
    print ("\nTotal population covered:", population)
    if ifPrint:    
        print ("%d filenames written: %s" % (len(filenames), filenames))
    return done

if __name__ == '__main__':

    # ts, bnn = dataFiles.data(withSynthetic=True)
    # dates = dataMangling.dates_list(ts)
    dm = dataMangling.dataMangled(withSynthetic=True)

    examples=True
    if examples:
        test_plot_Kreis(dm)
        test_plot_Bundesland(dm)
        test_plot_Bundesland(dm, Bundesland="Deutschland")

    longrunner=True
    if longrunner:    
        plot_Kreise(dm, dm.ts["AGS"].tolist())
        plot_all_Bundeslaender(dm)
        


