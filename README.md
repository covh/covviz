# covid19 time series visualization - districts of Germany
generates a static website from daily updated infections data in Germany.

### start here:

[index.html](index.html) and then [pages/about.html](pages/about.html)

### install dependencies
virtual env:
```
python3 -m venv ./py3science
source ./py3science/bin/activate
pip3 install -U pip wheel
pip install -r requirements.txt
ipython kernel install --user --name="py3science"
```

or try the newest versions of the Python dependencies (also helps if your system has an **older version of python**) :
```
deactivate
rm -r ./py3science
python3 -m venv ./py3science
source ./py3science/bin/activate
pip3 install -U pip wheel
pip3 install jupyter ipykernel numpy pandas matplotlib wget geopy requests beautifulsoup4 lxml
ipython kernel install --user --name="py3science"
```
but no guarantees then that my code will still work.

### execute
first time: important! downloads districts GPS positions, generates pairwise distances, creates all pages and pics once:

    sudo apt install expect # or remove the 2 'unbuffer' commands from the following script, and just be patient:
    ./scripts/initialize.sh

later: pull code & site; recreate site, copy content into cov19de repo, git-add-commit-push, done. 

    ./scripts/downloadAndUpdate.sh
    
That script also shows some initial insights into the newest data already.

### interactive notebook - runs Python in your browser!

experimental: 

* first try working with the raw data: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/covh/covviz/master?filepath=notebooks%2Frisklayer-pandas.ipynb) (starts a Jupyter notebook, with the whole repo preloaded, all dependencies installed, etc.).

### see also:

[todo.md](todo.md), [history.txt](history.txt), [log.txt](log.txt)

