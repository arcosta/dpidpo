import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt


authorsVector = list()
authorsVectorBackup = []
authorsListId = list()
relationVector = []
teste = ["A", "B", "C"]
teste2 = ["Paulo", "Aurelio", "Dalton", "André", "Ayrton", "Julio", "Aline"]

# Importa arquivo .csv
scopus_csv = pd.read_csv('teste.csv')


# Desmebra a coluna de "Authors" e cria um vetor com os autores
for line in scopus_csv["Authors"]:
    authors = line.split(',')
    for author in authors:
        authorsVector.append(author)


# Atribui um id e afiliação para cada autor || nome_autor | id_autor | affil_autor||
i = 0
for item in authorsVector:
    authorsListId.append([authorsVector[i], i+1])
    i += 1

end = len(authorsVector)

# Cria o relacionamento de todos com todos para a produção
for j in range(end):
    for item in authorsVector:
        if(authorsVector[j] != item and item != ''):
            relationVector.append([authorsVector[j], item])
    authorsVector[j] = ''


f = open('gephi.csv', 'w')
with f:
    writer = csv.writer(f)
    writer.writerow(['author', 'coauthor'])
    for row in relationVector:
        writer.writerow(row)

df = pd.read_csv("gephi.csv")
df.head()

graph = nx.from_pandas_edgelist(
    df, source='author', target='coauthor', edge_attr=None, create_using=None)

nx.draw(graph)
plt.show()
