#!/usr/bin/env python3
"""
@summary: simulate processing the data, visual inspectionl, etc 
          - BUT without copying into webfacing repo. 

@version: v03.4 (24/June/2020)
@since:   22/May/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@status:  more or less ready, doesn't need attention
"""

import daily

if __name__ == '__main__':
    
    daily.daily_update(publish=False, showExtremes=True, withSyntheticData=False)
    
    # daily.showSomeExtremeValues()
    
    print ("\nREADY.")
    