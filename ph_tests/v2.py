import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

authorsAffiliation = []
relationVector = []
teste = ["A", "B", "C"]
teste2 = ["Paulo", "Aurelio", "Dalton", "André", "Ayrton", "Julio", "Aline"]
author_id = 0
# Importa arquivo .csv
scopus_csv = pd.read_csv('teste.csv')
scopus_df = pd.DataFrame(scopus_csv)

lastRow = len(scopus_csv)

for k in range(lastRow):
    authorsVector = []
    authorsListId = []
    authorsAffiliation = []

    # Desmembra a coluna de "Authors" e cria um vetor com os autores
    authLine = scopus_csv["Authors"][k]
    authors = authLine.split(',')
    for author in authors:
        authorsVector.append(author)

    # Atribui um id e afiliação para cada autor || nome_autor | id_autor | affil_autor||
    for l in range(len(authorsVector)):
        print(l)
        author_id += 1
        authorsListId.append([authorsVector[l], author_id])

    print("VALOR", authorsListId)

    # Escreve .cvs de nós
    f = open('nodes.csv', 'a')
    with f:
        writer = csv.writer(f)
        for row in authorsListId:
            writer.writerow(row)
