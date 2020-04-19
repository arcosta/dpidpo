import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Importa arquivo .csv
scopus_csv = pd.read_csv('teste.csv')
scopus_df = pd.DataFrame(scopus_csv)

authorsVector = []
authorsListId = []
authorsAffiliation = []
relationVector = [""]
affiliationVector = []
affiliationColumn = []
unb = [
    "Universidade de Brasilia", "UnB", "Universidade de Brasília", "University of Brasilia"]

# Desmembra a coluna de "Authors" e cria um vetor com os autores
authLine = scopus_csv["Authors"][0]
authors = authLine.split(',')
for author in authors:
    authorsVector.append(author)

# Desmembra a coluna de "Affiliations"
affLine = scopus_csv["Authors with affiliations"][0]
affiliations = affLine.split(';')
for affiliation in affiliations:
    affiliationVector.append(affiliation)

# Pesquisa se autor é da UnB (1) ou de fora (0)
j = 0
for item in affiliationVector:
    print(j, item)
    if any(word in item for word in unb):
        affiliationColumn.insert(j, 1)
    else:
        affiliationColumn.insert(j, 0)
    j += 1

print(affiliationColumn)
