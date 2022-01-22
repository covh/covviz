#!/usr/bin/env python3
"""
@summary: download newest data, visual inspection, (if new data) generate plots, (always) generate pages, copy into webfacing repo, git push 

@version: v03.8.0 (02/May/2021)
@since:   22/May/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@status:  more or less ready, does NOT need attention.
"""


import daily

if __name__ == '__main__':
    
    daily.daily_update(regenerate_pages_regardless_if_new_data=True, 
                       showExtremes=True, 
                       withSyntheticData=False, 
                       getMasterSheet=False, 
                       publish=True)
    
    # daily.showSomeExtremeValues()
    
    print ("\nREADY.")
    