'''
Created on 25 Apr 2020

@author: andreas
'''

import os, datetime

import pandas
# import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling


def plot_timeseries(dates, daily, cumulative, title, filename, ifShow=True):

    fig, ax = plt.subplots(figsize=(14, 10)) #, constrained_layout=True)
    # plt.tight_layout()

    # x axis
    ax.xaxis_date()
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
    fig.autofmt_xdate(rotation=60)

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
    center, signal = dataMangling.temporal_center(daily)
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

    text = "source data @RiskLayer up to " + ("%s"%max(dates))[:10]
    text += "\nplot @DrAndreasKruger " + ("%s" % datetime.datetime.now())[:16]
    text += "\ndaily cases --> 'center date' = "+center_date

    plt.legend(lines, labs, loc='best', facecolor="white", framealpha=1, 
               title=text)

    plt.title(title)
    
    fig.savefig(os.path.join(dataFiles.PICS_PATH, filename),  bbox_inches='tight')
    
    if ifShow:
        plt.show()
        
    plt.clf()
    plt.close("all")


def test_plot_Kreis(ts, bnn, dates):
    ## Kreis
    AGS = "0"
    #AGS = "1001"
    #AGS = "5370"
    #AGS = "9377"
    daily, cumulative, title, filename = dataMangling.get_Kreis(ts, bnn, AGS)
    plot_timeseries(dates, daily, cumulative, title, filename=filename)


def plot_Kreise(ts, bnn, dates, Kreise_AGS):
    for AGS in Kreise_AGS:
        daily, cumulative, title, filename = dataMangling.get_Kreis(ts, bnn, AGS)
        plot_timeseries(dates, daily, cumulative, title, filename=filename, ifShow=False)
        print (title, filename)


def test_plot_Bundesland(ts, bnn, dates):
    ## Bundesland
    Bundesland = "Dummyland"
    Bundesland = "Hessen"
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    daily, cumulative, title, filename, population = dataMangling.get_BuLa(Bundeslaender, Bundesland)
    plot_timeseries(dates, daily, cumulative, title, filename=filename)


def plot_all_Bundeslaender(ts, bnn, dates):
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    filenames, population = [], 0
    for BL in Bundeslaender.index.tolist():
        print (BL, end=" ")
        daily, cumulative, title, filename, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL)
        if BL=="Deutschland":
            filename = filename.replace("bundesland_", "")
        plot_timeseries(dates, daily, cumulative, title, filename=filename, ifShow=False)
        filenames.append(filename)
        population += pop_BL
    print ("\nTotal population covered:", population)
    print ("%d filenames written: %s" % (len(filenames), filenames))

if __name__ == '__main__':

    ts, bnn = dataFiles.data(withSynthetic=True)
    dates = dataMangling.dates_list(ts)
    
    #test_plot_Kreis(ts, bnn, dates)
    
    plot_Kreise(ts, bnn, dates, ts["AGS"].tolist())
    
    #test_plot_Bundesland(ts, bnn, dates)
    # plot_all_Bundeslaender(ts, bnn, dates)
        

