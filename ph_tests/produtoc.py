import csv
import pandas as pd
import numpy as np
import json
import csv

authorVector = list()
coautor = list()
placeVector = list()
coauthorLine = list()
coauthorsArray = list()
relation = {}
data = {}
place = ''
authorSearched = ''


# Importa arquivo .csv
data = pd.read_csv('scopus.csv')

# Desmebra a coluna de "Authors" e cria um vetor com os autores
for line in data["Authors"]:
    authors = line.split(',')
    for author in authors:
        authorVector.append(author)

# Prepara as colulas de autores e coautores
df = pd.DataFrame(data)
columAuthor = pd.DataFrame(df["Authors"])
columCoAuthor = pd.DataFrame(df["Authors with affiliations"])

# Pesquisa em que linha da coluna de autores se encontra o autor


def findIdx(df, pattern):
    for author in columAuthor:
        return [pattern, columAuthor.astype('str').apply(lambda x: x.str.contains(pattern)).values.nonzero()]


# Retorna a linha em que o autor foi encontrado
coordenates = findIdx(columAuthor, r"Giozza W.F.")
authorSearched = coordenates[0]
coauthorLine.append(coordenates[1][0])
lineVec = coauthorLine[0]
lineNumber = lineVec[0]

# Retorna os coautores do autor em cada produção
for line in coauthorLine:
    coauthorsArray.append(columCoAuthor.loc[lineNumber])

    dataf = pd.DataFrame(coauthorsArray)

    coauthors_list = dataf.values.tolist()
    relation = {authorSearched: coauthors_list}

with open('author_coauthors.txt', 'w') as outfile:
    json.dump(relation, outfile)
