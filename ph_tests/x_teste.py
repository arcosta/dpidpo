import regex
import pandas as pd
import csv

# Importa arquivo .csv
scopus_csv = pd.read_csv('scopus.csv')
scopus_df = pd.DataFrame(scopus_csv)

print(scopus_df['Year'][0])
