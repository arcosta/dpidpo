import pandas as pd
import numpy as np
import re
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
words = ''


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

    coauthors_list_vector = dataf.values.tolist()
    coauthors_list = coauthors_list_vector[0]
    relation = {
        "author": authorSearched,
        "coauthors": coauthors_list[0]
    }


# Cria .json com autor->coautores  [Podemos usar para alimentar wikidata]
with open('author_coauthors.txt', 'w') as outfile:
    json.dump(relation, outfile)

# Tratamento de dados para criar rede de autor-coautores (csv)
coauthVector = coauthors_list[0].split(';')


f = open('gephi.csv', 'w')

with f:

    writer = csv.writer(f)

    for coAuth in coauthVector:
        auth = "%s" % authorSearched
        nms = [[str(auth), coAuth]]
        for row in nms:
            writer.writerow(row)
