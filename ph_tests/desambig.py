import pandas as pd
import csv
import json


lattes_table = list()  # vetor nome,[variações]
line_dataframe = list()
author_vector = list()
match = 0
noMatch = 0

j = 0

# Importa arquivo .csv e converte em dataframe
lattes_csv = pd.read_csv('lattes.csv')
scopus_csv = pd.read_csv('scopus.csv')

scopus = pd.DataFrame(scopus_csv)

lattes_df = pd.DataFrame(lattes_csv)
lattes = lattes_df.drop(["Currículo Lattes"], axis=1)


# Desmebra a coluna de "Authors" e cria um vetor com os autores
for line in scopus["Authors"]:
    authors = line.split(',')
    for author in authors:
        author_vector.append(author)

# Desmebra a coluna com as variações de nome e cria um vetor com elas
for line in lattes["Nome em Citações Bibliográficas"]:
    lattes_vector = list()
    aux_vec = list()

    authors = line.split(';')
    for name in authors:
        lattes_vector.append(name)
    lattes_table.append([lattes.iloc[[j], [0]], lattes_vector])


# Faz a desambiguação com base no lattes
    i = 0
    for author in author_vector:
        if any(word in author for word in lattes_table[j][1]):
            print(author, lattes_table[j][1])
            author_vector[i] = lattes_table[j][0].values
            match += 1
        else:
            noMatch += 1
        i += 1
    j += 1

print(match, noMatch)
f = open("data_frame_lattes.csv", "w")
with f:
    writer = csv.writer(f)
    for row in author_vector:
        writer.writerow([row])
