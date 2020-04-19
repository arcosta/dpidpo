import pandas as pd
import networkx as nx
import glob
import os
import re
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class WoS(object):
  def __init__(self):
    self.coauthors = nx.Graph()

  def search(self, query=''):
    pass

  def load_csv(self):
    logging.debug("Carregando os seguintes arquivos ",
      " ".join(glob.glob(os.path.join('data', "savedrecs-4*.txt")))
      )
    df = pd.concat(
      map(
        lambda file: pd.read_csv(file, 
                        sep='\t', 
                        header=0, 
                        encoding='utf-8-sig', 
                        index_col=False, 
                        dtype=str, 
                        na_values="", 
                        keep_default_na=False, 
                        na_filter=False), 
        glob.glob(os.path.join('data', "savedrecs-4*.txt"))
        )
      )

    affiliations = WoS.resolv_affiliation(df, "C1")
    aliases_index = WoS.create_aliases_index()

    logging.debug("Processing authorship")
    for row in df[['AF', 'PY']].values:
      
      pub_year = int(row[1])
      authors = list(map(str.strip, row[0].split(';'))) 
      start = pub_year
      stop = pub_year       
        
      for author in authors:
        author_label = aliases_index.get(author, author)
        try:
          aff = affiliations[author]
          
          if self.coauthors.has_node(author):
            start = self.coauthors.node[author]['start'] if pub_year > self.coauthors.node[author]['start'] else pub_year
            stop = self.coauthors.node[author]['stop'] if pub_year < self.coauthors.node[author]['start'] else pub_year
          else:
            if aff.find('Univ Brasilia') >=0:
              self.coauthors.add_node(author, label = author_label, start = start, stop = stop, affiliation=aff, color='#00FF00')
            else:
              self.coauthors.add_node(author, label = author_label, start = start, stop = stop, affiliation=aff)
        except KeyError:
          self.coauthors.add_node(author, label = author_label, start = start, stop = stop)

        for u in authors:
          for v in authors:
            if u != v:
              self.coauthors.add_edge(u, v, start=str(pub_year), stop=2021)

    
  def write_gexf(self, outfile="data\\wos.gexf"):
    logging.debug(f"Saving network to {outfile}")
    nx.write_gexf(self.coauthors, outfile)

  @staticmethod
  def create_aliases_index():
    result = dict()
    df2 = pd.read_csv("D:\\devel\\dpidpo\\data\\Coleta Outros Nomes  - Lattes (DPI_DPO) - Página1.csv",
              header=0,
              index_col=False
              )
    for row in df2[['Nome','Nome em Citações Bibliográficas']].values:
      name = row[0]
      aliases = row[1].split(';')
      for alias in aliases:
        result[alias] = name
    return result

  @staticmethod
  def resolv_affiliation(df, column_aff):
    '''
    @description: Extract the affiliation data of authors
    @return: A dict with authors name as keys
    '''
    logging.debug("Resolving affiliations")
    result = {}
    for row in df[column_aff]:
      try:
        if row.find('[') < 0:
          for author_address in row.split(';'):
            name = ''.join(author_address.split(',')[:2])
            address = ''.join(author_address.split(',')[2:]).strip()
            result[name] = address
        else:
          authors_addr = row.split('; [')
          for inner_author_addr in authors_addr:
            authors,addr = inner_author_addr.split('] ')
            for author in authors.split(';'):
              result[author] = addr
      except ValueError as err:
        print(f"Erro {err} ao encontrar filiação na linha: {row}")
      except AttributeError as err:
        print(f"Erro {err} ao encontrar filiação na linha: {row}")
    return result




  
