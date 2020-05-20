import pandas as pd
import networkx as nx
import glob
import os
import re
import logging
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


class WoS(object):
  def __init__(self):
    self.coauthors = nx.Graph()

  def search(self, query=''):
    pass

  def load_csv(self):
    logging.debug(
      "Carregando os seguintes arquivos "+str(glob.glob(os.path.join('data', "savedrecs-*.txt")))
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
        glob.glob(os.path.join('data', "savedrecs-*.txt"))
        )
      )      
      
    logging.debug(f"DataFrame shape: {df.shape}")

    logging.debug("Resolvendo filiações")
    affiliations = WoS.resolv_affiliation(df, "C1")

    logging.debug("Criando índice de apelidos")
    aliases_index = WoS.create_aliases_index()

    logging.debug("Processando autoria de publicações")
    for row in df[['AF', 'PY']].values:
      pub_year = 0  
      try:
        pub_year = int(row[1])
      except ValueError:
        pub_year = 1950
      authors = list(map(str.strip, row[0].split(';'))) 
      start = pub_year
      stop = pub_year       
        
      for author in authors:
        author_label = aliases_index.get(author, author)
        try:
          aff = affiliations[author]
          
          if self.coauthors.has_node(author):
            start = self.coauthors.node[author]['spells'][0][0] if pub_year > self.coauthors.node[author]['spells'][0][0] else pub_year
            stop = self.coauthors.node[author]['spells'][0][1] if pub_year < self.coauthors.node[author]['spells'][0][1] else pub_year
            self.coauthors.node[author]['numpub'] = self.coauthors.node[author]['numpub'] + 1
          else:
            if aff.find('Univ Brasilia') >=0:
              self.coauthors.add_node(author, label = author_label, numpub=1, spells=[(start, stop)], affiliation=aff, color='#00FF00')
            else:
              self.coauthors.add_node(author, label = author_label, numpub=1, spells=[(start, stop)], affiliation=aff)
        except KeyError:
          self.coauthors.add_node(author, label = author_label, numpub=1, spells=[(start, stop)])

      for u in authors:
        for v in authors:
          if u != v:
            if self.coauthors.has_edge(u,v) is False:
              self.coauthors.add_edge(u, v, spells=[(start, stop)])
            else:
              spells = set(self.coauthors[u][v]['spells'])
              spells.add((start, stop))
              self.coauthors[u][v]['spells'] = spells

  @timeit  
  def write_gexf(self, outfile="data\\wos.gexf", version='1.2draft'):
    logging.debug(f"Salvando rede social no arquivo: {outfile}")
    nx.write_gexf(self.coauthors, outfile, version=version)

  @timeit
  def merge_nodes(self):
    for node in self.coauthors.nodes_iter():
      for alias in list(self.generate_abbreviations(node)):
        if self.coauthors.has_node(alias):
          logging.debug(f"Merging nodes {node} {self.coauthors.node[alias]}")
          self.coauthors = nx.contracted_nodes(self.coauthors, node, [n for n in self.coauthors.nodes() if n==alias][0])

  def generate_abbreviations(self, name):
    if name.find('.') > 0 or name.find(',') < 0 or name.count(',') > 1:
      return
    name = name.strip()
    surname = ''
    first_name = ''
    try:
      (surname, first_name) = name.split(',')
    except ValueError:
      print("Tentativa de dividir ", name)
      raise("Erro ao processar nome para abreviação")
    first_name = first_name.strip() 
    space_index = first_name.find(' ')
    prefix = surname+', '
    if space_index > 0:
      cap_1 = first_name[0]
      cap_2 = first_name[space_index+1]
      yield prefix+cap_1+cap_2
      yield prefix+cap_1+'. '+cap_2+'.'
      yield prefix+first_name[:space_index]+' '+cap_2+'.'
    else:
      yield f"{prefix}{first_name[0]}."
      
    
  @staticmethod
  def create_aliases_index():
    '''
    @description: Cria e retorna um dicionario com cada nome usado para citação pelos autores
    @return Um dicionário indexado por cada apelido detectado no curriculo lattes
    '''
    result = dict()
    try:
      df2 = pd.read_csv(
        "D:\\devel\\dpidpo\\data\\Coleta Outros Nomes  - Lattes (DPI_DPO) - Página1.csv",
                header=0,
                index_col=False
                )
      for row in df2[['Nome','Nome em Citações Bibliográficas']].values:
        name = row[0]
        aliases = row[1].split(';')
        for alias in aliases:
          result[alias] = name
    except:
      logging.error("Erro ao tentar resolver aliases")
    return result

  @staticmethod
  def resolv_affiliation(df, column_aff):
    '''
    @description: Extract the affiliation data of authors
    @return: A dict with authors name as keys
    '''
    logging.debug("Resolvendo afiliação dos pesquisadores")
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
