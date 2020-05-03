'''
Created on 28 Apr 2020

@author: andreas
'''

import os, datetime, shutil, subprocess

import dataFiles, dataMangling, dataPlotting, districtDistances, dataTable, dataPages
from dataFiles import PICS_PATH, PAGES_PATH, WWW_REPO_PICS, WWW_REPO_PAGES, WWW_REPO_PATH, WWW_REPO_PATH_GIT_SCRIPT, REPO_PATH, ALSO_TO_BE_COPIED

def generate_all(alsoDoThePlots=True):
    
    dataFiles.downloadData()
    
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.dataMangled(withSynthetic=True)
    print()

    if not alsoDoThePlots:
        a="\n" + ("*"*50) + "\n"
        print (a+"ALERT: skipping the plots"+a)
    else:
        done = dataPlotting.plot_all_Bundeslaender(ts, bnn, dates, datacolumns, ifPrint=False)
        print ("plot_all_Bundeslaender: %d items" % len(done))
        
        listOfAGSs = ts["AGS"].tolist()
        print ("Plotting %d images, for each Kreis. Patience please: " % len(listOfAGSs))
        done = dataPlotting.plot_Kreise(ts, bnn, dates, datacolumns, listOfAGSs, ifPrint=False)
        print ("plot_Kreise done: %d items" % len(done))
        print()

    distances = districtDistances.load_distances()
    cmap = dataTable.colormap()
    
    Bundeslaender_filenames = dataPages.Bundeslaender_alle(Bundeslaender_sorted, ts, ts_sorted, datacolumns, bnn, distances, cmap, km=50);
    print (Bundeslaender_filenames)
    
    fn = dataPages.Deutschland(Bundeslaender_sorted, datacolumns, cmap, ts_sorted, bnn )
    print ("\n" + fn)
    
    print ("\nFinished at", ("%s" % datetime.datetime.now()) [:19])
    
    return True


def copy_all():
    print (os.getcwd()) 
    fromTo = [[PICS_PATH, WWW_REPO_PICS], 
              [PAGES_PATH, WWW_REPO_PAGES]]
    for s, d in fromTo:
        try:
            shutil.rmtree(d)
        except:  # ignore error if not existed
            pass
        dst = shutil.copytree(s, d)
        print (dst)
        os.remove(os.path.join(d, ".gitignore"))

    for single_file in ALSO_TO_BE_COPIED:
        dst = shutil.copy(os.path.join(REPO_PATH, single_file), WWW_REPO_PATH)
        print (dst)
    
    return True
    
def git_commit_and_push(path=WWW_REPO_PATH, script=WWW_REPO_PATH_GIT_SCRIPT):
    print ("\ngit script '%s' please be patient ..." % script)
    try:
        before = os.getcwd()
        os.chdir(path)
        answer = subprocess.check_output([script], shell=True)
    except Exception as e:
        print ("git ERROR:", type(e), e)
        return False
    else:
        print (answer.decode("utf-8"))
        return True
    finally: 
        os.chdir(before)


def daily_update(regenerate_all_plots_and_pages=True, alsoDoThePlots=True):
    print ("Started at", ("%s" % datetime.datetime.now()) [:19],"\n")
    
    success1, success2, success3 = False, False, False
    
    if regenerate_all_plots_and_pages:
        success1 = generate_all(alsoDoThePlots)
    
    if success1 or not regenerate_all_plots_and_pages:
        success2 = copy_all()
        
        if success2:
            print ()
            success3 = git_commit_and_push()
            print ("successful" if success3 else "not successful")
            
    print ("regenerate: %s, copy: %s, git push: %s" % (success1, success2, success3))
    
    print ("Finished at", ("%s" % datetime.datetime.now()) [:19],"\n")
    
    


if __name__ == '__main__':
    
    # git_commit_and_push(); exit()
    
    daily_update(regenerate_all_plots_and_pages=False); exit()
    # daily_update(regenerate_all_plots_and_pages=True, alsoDoThePlots=False); exit()
    daily_update()
    
    