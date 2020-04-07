import pandas as pd
import csv

authorsVector = list()
authorsList = list()
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

end = len(authorsVector)

# Cria o relacionamento de todos com todos para a produção
for j in range(end):
    print(j)
    for item in authorsVector:
        if(authorsVector[j] != item and item != ''):
            relationVector.append([authorsVector[j], item])
    authorsVector[j] = ''


print(relationVector)
