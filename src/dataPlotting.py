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

import os, datetime, time
import  multiprocessing as mp
import pandas
# import numpy
from matplotlib import pyplot as plt
import matplotlib 


import dataFiles, dataMangling


def plot_timeseries(datacolumns, dates, daily, cumulative, title, filename, ifShow=True, ifCleanup=True, population=None, limitIncidencePerWeekPerMillion=500):

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
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    lns2 = ax.plot(dates, rolling_mean, label='daily: centered moving average %s days' % window, color='purple')
    window=14
    rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    lns3 = ax.plot(dates, rolling_mean, label='daily: centered moving average %s days' % window, color='orange', linewidth=4)
    # window=21
    # rolling_mean = pandas.DataFrame(daily).rolling(window=window, center=True).mean()
    # ax.plot(dates, rolling_mean, label='SMA %s days' % window, color='pink', linewidth=1)

    # plot center bar
    center, signal = dataMangling.temporal_center(daily)
    # print (center)
    center_date=datacolumns.values[int(round(center))]
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


def test_plot_Kreis(ts, bnn, dates, datacolumns):
    ## Kreis
    AGS = "0"
    #AGS = "1001"
    AGS = "5370"
    # AGS = "9377"
    daily, cumulative, title, filename, pop = dataMangling.get_Kreis(ts, bnn, AGS)
    plot_timeseries(datacolumns, dates, daily, cumulative, title, filename=filename, population=pop)


def plot_Kreise(ts, bnn, dates, datacolumns, Kreise_AGS, ifPrint=True):
    done = []
    for AGS in Kreise_AGS:
        daily, cumulative, title, filename, pop = dataMangling.get_Kreis(ts, bnn, AGS)
        plot_timeseries(datacolumns, dates, daily, cumulative, title, filename=filename, ifShow=False, population=pop)
        done.append((title, filename))
        if ifPrint:
            print (title, filename)
        else:
            print (".", end="")
            if len(done)%60 == 0:
                print()
    if not ifPrint:
        print()
    return done


def plot_Kreise_parallel(ts, bnn, dates, datacolumns, Kreise_AGS, ifPrint=True, force_sequentially=True):
    """
    one CPU should be left free for the system, and multiprocessing makes only sense for at least 2 free CPUs,
    so just call the non-parallel version if not enough CPUs are in the system
    
    Many thanks to jalsti for the basis of this https://github.com/covh/covviz/pull/1
    Timings (100 districts, 4 CPUs): sequential 107.6 seconds versus parallel 53.7 seconds. 
    
    Standalone fine. 
    However, when integrated into the daily() routine, the X server of my dev machine crashed (!) twice.
    So switching parallel OFF by default:   force_sequentially=True
    """
    available_cpus = mp.cpu_count() 
    leave_alone_cpus = 1
    wanted_cpus = available_cpus - leave_alone_cpus

    before=time.perf_counter()
    print ("\nAvailable_CPUs: %d" % available_cpus, end=" ")
    
    if force_sequentially or available_cpus < wanted_cpus or wanted_cpus < 2:
        print("so falling back to sequential mode.")
        done = plot_Kreise(ts, bnn, dates, datacolumns, Kreise_AGS, ifPrint)
        
    else:
        print("so we save some time with parallel processing, in %d processes." % wanted_cpus)

        done = []
        # setup process pool
        pool = mp.Pool(wanted_cpus)
        try:
            done = pool.starmap(plot_Kreise, 
                                [(ts, bnn, dates, datacolumns, [AGS], ifPrint) 
                                 for AGS in Kreise_AGS])
        except KeyboardInterrupt:
            # without catching this here we will never be able to manually stop running in a sane way
            pool.terminate()
        finally:
            pool.close()
            pool.join()

    print ("To generate these %d took %.1f seconds.\n" % (len(done), time.perf_counter()-before))

    return done


def test_plot_Bundesland(ts, bnn, dates, datacolumns, Bundesland = "Hessen"):
    ## Bundesland
    # Bundesland = "Dummyland"
    
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    daily, cumulative, title, filename, population = dataMangling.get_BuLa(Bundeslaender, Bundesland, datacolumns)
    plot_timeseries(datacolumns, dates, daily, cumulative, title, filename=filename)


def plot_all_Bundeslaender(ts, bnn, dates, datacolumns, ifPrint=True):
    ts_BuLa, Bundeslaender = dataMangling.join_tables_for_and_aggregate_Bundeslaender(ts, bnn)
    filenames, population = [], 0
    done=[]
    for BL in Bundeslaender.index.tolist():
        print (BL, end=" ")
        daily, cumulative, title, filename, pop_BL = dataMangling.get_BuLa(Bundeslaender, BL, datacolumns)
        if BL=="Deutschland":
            filename = filename.replace("bundesland_", "")
        plot_timeseries(datacolumns, dates, daily, cumulative, title, filename=filename, ifShow=False)
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
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled(withSynthetic=True)
    
    examples=False
    if examples:
        test_plot_Kreis(ts, bnn, dates, datacolumns)
        test_plot_Bundesland(ts, bnn, dates, datacolumns)
        test_plot_Bundesland(ts, bnn, dates, datacolumns, Bundesland="Deutschland")

    longrunner=True
    if longrunner:    
        plot_Kreise_parallel(ts, bnn, dates, datacolumns, ts["AGS"].tolist()) # [:100]) #, force_sequentially=True)
        plot_all_Bundeslaender(ts, bnn, dates, datacolumns)
        


