import requests
import networkx as nx
import sys
import csv
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

class Scopus(object):
    def __init__(self):
        self.access_token = ''
        self.coauthors = nx.Graph()
    def search(self, query='authlast(Dalton)%20and%20authfirst(Martins)'):
        params = {
            'httpAccept': 'application/json',
            'apiKey': self.access_token,
            'query': query
        }
        response = requests.get("https://api.elsevier.com/content/search/author", params=params)

        return response.text
    
    def load_csv(self):
        with open('data\\scopus.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in reader:
                authors = row['Author(s) ID'].split(';')
                self.coauthors.add_nodes_from(authors)
                for u in authors:
                    for v in authors:
                        if u != v:
                            self.coauthors.add_edge(u, v)
        nx.write_gexf(self.coauthors, "data\\scopus.gexf")
