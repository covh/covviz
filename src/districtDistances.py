'''
Created on 27 Apr 2020

@author: andreas
'''

import io, sys

import pandas
import requests
import geopy.distance
import wget

from dataFiles import DATA_PATH, OPENDATASOFT_URL01, OPENDATASOFT_URL02, OPENDATASOFT_PATH, DISTANCES_PATH 

def download_kreise_locations(url1=OPENDATASOFT_URL01, url2=OPENDATASOFT_URL02, out=OPENDATASOFT_PATH):
    print ("Downloading large table with Kreise locations. For infos see")
    print (url1)
    print ("Patience please ...", end=" ")
    filename = wget.download(url2, out=out)
    print ("Done -->", filename)
    return filename

def load_kreise_locations(filename = OPENDATASOFT_PATH):
    # s=requests.get(url2).content
    # LKG=pandas.read_csv(io.StringIO(s.decode('utf-8')), sep=';') # error_bad_lines=False)
    LKG=pandas.read_csv(filename, sep=';')
    # immediately drop non-Kreis row(s)
    LKG.dropna(subset=['Cca 2'],inplace=True)
    # turn AGS into integer:
    LKG["Cca 2"]=LKG["Cca 2"].astype(int)
    print ("Done downloading.")
    return LKG

def accelerate_lookup(LKG):
    # accelerate lookup
    AGS_to_geopoint=dict(LKG[["Cca 2","Geo Point"]].set_index("Cca 2").to_dict('series')["Geo Point"])
    print ("Done generating lookup dict")
    return AGS_to_geopoint


def geo_distance(AGS_to_geopoint, AGS1, AGS2):
    c1 = list(map(float,AGS_to_geopoint[AGS1].split(",")))
    c2 = list(map(float,AGS_to_geopoint[AGS2].split(",")))
    # print (c1, c2 )
    return geopy.distance.geodesic(c1, c2).kilometers


def make_distances_table(AGS_to_geopoint, all_AGS, filename=DISTANCES_PATH):
    headers = ['AGS1','AGS2','km']
    counter,countermax=0, len(all_AGS)*(len(all_AGS)-1)
    distances=pandas.DataFrame([], columns = headers)
    for AGS1 in all_AGS:
        for AGS2 in all_AGS:
            if AGS1>=AGS2:
                continue
            geodist = geo_distance(AGS_to_geopoint, AGS1, AGS2)
            row=pandas.Series([AGS1, AGS2, geodist], index=headers)
            distances=distances.append(row, ignore_index=True)
            row=pandas.Series([AGS2, AGS1, geodist], index=headers)
            distances=distances.append(row, ignore_index=True)
            counter+=2
            if not counter%500:
                print (counter, "/", countermax)

    print ("Done calculating distances. Len(table)=%d" % len(distances))

    distances["AGS1"]=distances["AGS1"].astype(int)
    distances["AGS2"]=distances["AGS2"].astype(int)
        
    print ("Distances are distributed like this:")
    print(distances["km"].describe())
    
    distances.sort_values("km", inplace=True)
    print("Done sorting.")
    
    distances.to_csv(filename, index=False)
    print ("Saved to", filename)
    return distances, filename

def load_distances(filename = DISTANCES_PATH):
    distances = pandas.read_csv(filename)
    return distances

def number_of_pairs_max_dist(distances, km):
    return len( distances[(distances.km<=km)] ) / 2

def nearby(distances, AGS, km):
    return distances[(distances.km<=km) & (distances.AGS1==AGS)]
    

if __name__ == '__main__':
    AGS1,km = 5370, 50
    generateNew = False
    if generateNew:
        
        filename = OPENDATASOFT_PATH
        # filename = download_kreise_locations()
    
        LKG = load_kreise_locations(filename)
        
        AGS_to_geopoint = accelerate_lookup(LKG)
        print ("sample distance", geo_distance(AGS_to_geopoint, 1001, 1002))
    
        all_AGS=LKG["Cca 2"].dropna().astype(int).tolist()
        # all_AGS=all_AGS[:40] # reduce number for dev'ing
        print("now pairwise distances for %d locations" % len(all_AGS))
        print()
        
        distances, filename = make_distances_table(AGS_to_geopoint, all_AGS)
        
        AGS1, km = all_AGS[0], 150
        print("testing with AGS=%d and km=%d:" % (AGS1, km))
        print (distances[(distances.km<km) & (distances.AGS1==AGS1)])

    distances = load_distances()
    AGS1,km = distances["AGS1"][0], 50
    print ("\nwhole table contains %d pairs with distance max %.1f km" % (number_of_pairs_max_dist(distances, km), km))
    print ("example for AGS1=" , AGS1)
    print (nearby (distances, AGS1, km))
    
    

