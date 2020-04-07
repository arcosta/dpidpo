import pandas as pd
import csv

authorsVector = list()
authorsList = list()
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

end = len(authorsVector)

# Cria o relacionamento de todos com todos para a produção
for j in range(end):
    for item in authorsVector:
        if(authorsVector[j] != item and item != ''):
            relationVector.append([authorsVector[j], item])
    authorsVector[j] = ''

# Atribui um id para cada autor
i = 0
for item in teste:
    authorsListId.append([teste[i], i+1])
    i += 1


print(authorsListId)
