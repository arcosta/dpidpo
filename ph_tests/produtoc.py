import csv
import pandas as pd
import numpy as np
import json

authorVector = list()
coautor = list()
placeVector = list()
data = {}
place = ''

data = pd.read_csv('ph_tests/scopus.csv')

for line in data["Authors"]:
   authors = line.split( ',' )
   for author in authors:
       authorVector.append(author)

df = pd.DataFrame(data)
columAuthor = pd.DataFrame(df["Authors"])

def findIdx(df, pattern):
    for line in columAuthor:     
        return columAuthor.astype('str').apply(lambda x: x.str.contains(pattern)).values.nonzero()
    

#print(type(df))

coordenates = findIdx(columAuthor, r"Giozza")
print(coordenates[0])


