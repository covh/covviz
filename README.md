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

or redo the virtual env, then try the newest versions of the dependencies:
```
deactivate
rm -r ./py3science
python3 -m venv ./py3science
source ./py3science/bin/activate
pip3 install -U pip wheel
pip3 install jupyter ipykernel numpy pandas matplotlib wget geopy requests
ipython kernel install --user --name="py3science"
```
but no guarantees then that my code will still work.

### execute
recreate site, copy content into cov19de repo, git-add-commit-push, done. 

	cd src
	python3 daily.py
    
Finally also shows some initial insights into the newest data already.

### see also:

[todo.md](todo.md), [history.txt](history.txt), [log.txt](log.txt)

