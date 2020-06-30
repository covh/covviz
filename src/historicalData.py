#!/usr/bin/env python3
"""
@summary: download old versions of the 'Haupt' sheet  

@version: v03.5 (27/June/2020)
@since:   24/May/2020

@author:  Dr Andreas Krueger
@see:     https://github.com/covh/covviz for updates

@status:  more or less ready, doesn't need attention
"""

import dataFiles

VERSION_HISTORY_TABLE = {"sheetID"   : "1rn_nPJodxAwahIzqfRtEr9HHoqjvmh_7bj6-LUXDRSY",
                         "sheetName" : "ThePast",
                         "range" :     "A3:E12"}

if __name__ == '__main__':
    
    dataFiles.get_haupt_sheet_ids_then_download_all(sheet=VERSION_HISTORY_TABLE)
    
    print ("\nREADY.")
    