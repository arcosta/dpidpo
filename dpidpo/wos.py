import csv
import networkx as nx

class WoS(object):
  def __init__(self):
    self.coauthors = nx.Graph()
  def search(self, query=''):
    pass
  def load_csv(self):
    with open('data\\savedrecs 2.tsv') as tsvfile:
      reader = csv.DictReader(tsvfile, dialect='excel-tab')
      for row in reader:
        authors = row['AU'].split(';')
        self.coauthors.add_nodes_from(authors)
        for u in authors:
          for v in authors:
            if u != v:
              self.coauthors.add_edge(u, v)
    nx.write_gexf(self.coauthors, "data\\wos.gexf")

