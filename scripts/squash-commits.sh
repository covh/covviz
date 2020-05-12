# careful this is not debugged yet, also it is interactive

# see https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History#The-Nuclear-Option:-filter-branch

git checkout 8185d41999bbde00aecf2e56be245997c138fd24
git rebase -i 8185d41999bbde00aecf2e56be245997c138fd24

pick e695f89c9885fc5343a34fc470f2fe43a66adb32 20200506-0526
squash 8185d41999bbde00aecf2e56be245997c138fd24 20200506-0549

# doesn't work yet.
# If anyone knows how to do this, please help.
# I want to squash many commits into one - perhaps one for each day?

# perhaps this might help:
# but first try on a COPY of the repo !!
# https://stackoverflow.com/questions/56851561/how-to-automate-git-history-squash-by-date/56852575#56852575
