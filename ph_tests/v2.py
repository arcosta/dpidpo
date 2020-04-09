import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

authorsAffiliation = []
relationVector = []
unb = [
    "Universidade de Brasilia", "UnB", "Universidade de Brasília", "University of Brasilia", "University of Brasília", "Universidáde de Brasília"]
author_id = 0
# Importa arquivo .csv
scopus_csv = pd.read_csv('teste.csv')
scopus_df = pd.DataFrame(scopus_csv)

lastRow = len(scopus_csv)

authorsListId = []
relationVector = []
affiliationColumn = []


for k in range(lastRow):
    authorsVector = []
    authorsAffiliation = []
    affiliationVector = []

    # Desmembra a coluna de "Authors" e cria um vetor com os autores
    authLine = scopus_csv["Authors"][k]
    authors = authLine.split(',')
    for author in authors:
        authorsVector.append(author)

    # Desmembra a coluna de "Affiliations with affiliations"
    affLine = scopus_csv["Authors with affiliations"][k]
    affiliations = affLine.split(';')
    for affiliation in affiliations:
        affiliationVector.append(affiliation)

    # Pesquisa se autor é da UnB (1) ou de fora (0)
    j = 0
    for item in affiliationVector:
        if any(word in item for word in unb):
            affiliationColumn.insert(j, 1)
        else:
            affiliationColumn.insert(j, 0)
        j += 1

    # Atribui um id e afiliação para cada autor || nome_autor | id_autor | affil_autor||
    for l in range(len(authorsVector)):
        author_id += 1
        authorsListId.append(
            [author_id, authorsVector[l], affiliationColumn[l]])

    # Cria o relacionamento de todos com todos para a produção
    for j in range(len(authorsVector)):
        for item in authorsVector:
            if(authorsVector[j] != item and item != ''):
                relationVector.append([authorsVector[j], item])
        authorsVector[j] = ''


# Escreve .cvs de nós
f = open('nodes.csv', 'a')
with f:
    writer = csv.writer(f)
    for row in authorsListId:
        writer.writerow(row)

f = open('edges.csv', 'a')
with f:
    writer = csv.writer(f)
    for row in relationVector:
        writer.writerow(row)
