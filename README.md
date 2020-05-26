# covid19 time series visualization - districts of Germany
generates a static website from daily updated infections data in Germany.

### start here, to learn about the purpose of the project

[index.html](https://covh.github.io/cov19de/index.html) and then [pages/about.html](https://covh.github.io/cov19de/pages/about.html)

## architecture:
* covh/covviz = code. Python, bash scripts, instructions, static pages, etc = sparse, small, lots of .gitignore.
* covh/cov19de = site. Copies of all (generated & static) HTML pages, plot images, etc = the github pages at [covh.github.io/cov19de](https://covh.github.io/cov19de)  

If you want to work with this, and make your own copy of the site, fork both repositories. Swap out `covh` for your username everywhere below.

### dependencies, clone, install
needed machine wide dependencies: git for github, virtualenv for python, expect for unbuffer

    sudo apt install git python3-venv expect 

(IF you may not install software, but have git & venv installed already - you can ignore expect, and remove the `unbuffer` command later)

clone both repos, they MUST be besides each other, then enter the code repo 'covviz':
```
mkdir covh
cd covh
git clone https://github.com/covh/covviz.git
git clone https://github.com/covh/cov19de.git

cd covviz
```

virtual env with the *proven* dependencies versions given in requirements.txt
```
python3 -m venv ./py3science
source ./py3science/bin/activate
pip3 install -U pip wheel
pip install -r requirements.txt
ipython kernel install --user --name="py3science"
```

OR try the *newest* versions of the Python dependencies (also helps if your system has an **older version of Python**) :
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

    ./scripts/initialize.sh

later: pull code & site; recreate site, copy content into cov19de repo, git-add-commit-push, done. 

    ./scripts/downloadAndUpdate.sh
    
That script also shows some initial insights into the newest data already.

#### git push
git push (the last step of `downloadAndUpdate.sh`) will only properly work if you have write access to the repo, i.e. you must adapt the following to *your fork* of that repo (for example, swap out `covh` for *your* github username), and you must create and [upload an SSH key, see here](https://github.com/settings/keys), then edit the `.git config` of your site repo fork: 

    gedit covh/cov19de/config

and change it so that it contains something like this:

```
...
[remote "origin"]
	url = git@github.com:covh/cov19de.git
	...
...
[user]
    name = Your Name
    email = your@email.address
```

Run this simple script (after editing any file in that repo) in the site repo, to try out whether the ssh git push works:

[./git-add-commit-push.sh](https://github.com/covh/cov19de/blob/master/git-add-commit-push.sh)

If it does, your last step is to configure the github pages, in YOUR fork of https://github.com/covh/cov19de/settings (i.e. with `covh` changed to your username), to "Source master branch = Your GitHub Pages site is currently being built from the master branch."

Done.


## interactive notebook - runs Python in your browser!

experimental: 

* first try working with the raw data: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/covh/covviz/master?filepath=notebooks%2Frisklayer-pandas.ipynb) (starts a Jupyter notebook, with the whole repo preloaded, all dependencies installed, etc.).

## see also:

[todo.md](todo.md), [history.txt](history.txt), [log.txt](log.txt)

