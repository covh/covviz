import os, sys, timeit
import bottle, pandas # pip install bottle pandas
from bottle import route, template, redirect, static_file, error, run
from io import StringIO
import dataFiles, daily, dataMangling

STATIC_ROOT = 'static'

# trick as heroku's root is repo root, not src: go down into folder, so that "go up" = .. then works
BNN_FILE=os.path.join("src", dataFiles.BNN_FILE)
 
# current directory the src folder? Happens on local machine:
if "src" == os.getcwd().split(os.sep)[-1]:  
    bottle.TEMPLATE_PATH.insert(0, '../views') # corrects path for local machine
    STATIC_ROOT = os.path.join("..", STATIC_ROOT)
    BNN_FILE=dataFiles.BNN_FILE


@route('/home')
def show_home():
    return template('home')


@route('/')
def handle_root_url():
    redirect('/home')


# TODO: put this elsewhere:

title=daily.title

def CSV_download_and_inspect_verbose(url=dataFiles.RISKLAYER_URL01):
    before=timeit.default_timer()
    ts = dataFiles.downloadDataNotStoring(url)
    downloadTime=timeit.default_timer() - before 
    print ("\ndownloaded timeseries CSV DataFrame size: %s x %s" % (len(ts.columns), len(ts)))
    ts = dataFiles.attribution_and_repair(ts)
    print (title("inspect data - e.g. show negative daily growth, totals, diffs, etc."))
    print ("(too many daily negatives can be a sign of data corruption - was useful e.g. on 29/May/2020)")
    dataFiles.inspectNewestData(ts, alreadyRepaired=True)
    # raise Exception("Simulated Error")
    bnn=pandas.read_csv(BNN_FILE)
    ts, bnn, ts_sorted, Bundeslaender_sorted, dates, datacolumns = dataMangling.additionalColumns(ts,bnn)
    daily.showSomeExtremeValues(ts_sorted, datacolumns, n=15)
    daily.showBundeslaenderRanked(Bundeslaender_sorted, datacolumns, rankedBy="incidence_1mio_last7days")
    processingTime=timeit.default_timer() - before - downloadTime
    print(title("END. Timing: downloading=%.2f seconds, processing=%.1f seconds" %(downloadTime, processingTime)))

def print_error_and_suggestions(e, url):
    print (type(e), e)
    print ("\nThis is NOT good.\nSomething's wrong with the input CSV: ", url)
    print(" Solution 1: Instructions how to inspect it at: https://covh.github.io/cov19de/pages/risklayer-data.html")
    print(" Solution 2: Perhaps simply come back in >24 hours? FAILING for now. Sorry - and ... have a good day :-)")

@route('/csvtest')
def csvtest(url=dataFiles.RISKLAYER_URL01):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        CSV_download_and_inspect_verbose(url)
    except Exception as e:
        print (title("ERROR"))
        print_error_and_suggestions(e, url)

    sys.stdout = old_stdout
    data = mystdout.getvalue()
    return template('csvtest', output=data)


@route('/css/<filename>')
def send_css(filename):
    return static_file(filename, root=os.path.join(STATIC_ROOT, 'css'))


@error(404)
def error404(error):
    return template('error', error_msg='404 error. Nothing to see here')


##################################################################

if "heroku" in os.environ.get('PYTHONHOME', ''):
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=8080, debug=True)
