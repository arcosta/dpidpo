import csv
import pandas as pd
import numpy as np
import json

authorVector = list()
coautor = list()
placeVector = list()
data = {}
place = ''

data = pd.read_csv('teste2.csv')

for line in data["Authors"]:
   authors = line.split( ',' )
   for author in authors:
       authorVector.append(author)

df = pd.DataFrame(data)
columAuthor = pd.DataFrame(df["Authors"])

for row in columAuthor["Authors"]:
    nocommas = row.replace(',', "")
    place = nocommas.replace('.', "")
    place = place.replace(' ', "")
    placeVector.append(place)
    
place = pd.DataFrame(placeVector)
print(place)

def findIdx(df, pattern):
    for line in columAuthor:      
        return np.transpose(place.astype('str').apply(lambda x: x.str.contains(pattern)).values.nonzero())
    

#print(type(df))
#print(type(columAuthor))
coordenates = findIdx(place, r"Portela")
print(coordenates)

