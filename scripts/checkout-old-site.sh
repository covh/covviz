# clone the whole repo (900 MB on May 12th)
# note: hard size limit is 100 GB https://help.github.com/en/github/managing-large-files/what-is-my-disk-quota#file-and-repository-size-limitations
# but it is nicer to reduce when 1 GB is reached.
git clone https://github.com/covh/cov19de.git
cd cov19de



# choose one here https://github.com/covh/cov19de/commits/master
git checkout af9422e24c6af3b73621f55d2414a05a62d5e2d9

# old site
open index.html

# compare with current site
xdg-open https://tiny.cc/cov19de &
