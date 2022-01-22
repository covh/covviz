#!/usr/bin/env python3
"""
@summary: download newest data, visual inspection, 
          (if new data) generate pages, (always) generate plots,  
          (perhaps DO NOT, depends on publish=) copy into webfacing repo, git push 

@version: v03.9.1 (22/Jan/2022)
@since:   22/May/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@status:  more or less ready, does NOT need attention.
"""


import daily

if __name__ == '__main__':
    
    daily.daily_update(regenerate_pages_regardless_if_new_data=False,
                       regenerate_plots_regardless_if_new_data=True,
                       showExtremes=True, 
                       withSyntheticData=False, 
                       getMasterSheet=False, 
                       publish=False)
    
    # daily.showSomeExtremeValues()
    
    print ("\nREADY.")
    