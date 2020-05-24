'''
Created on 22 May 2020

@author: andreas
'''

import daily

if __name__ == '__main__':
    
    daily.daily_update(publish=False,
                       regenerate_pages_regardless_if_new_data=True,
                       regenerate_plots_regardless_if_new_data=True,
                       showExtremes=False,
                       withSyntheticData=False)
   
    print ("\nREADY.")
    