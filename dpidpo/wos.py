import pandas as pd
import glob
import os
import re
import logging
import sys
import time
import csv
import pickle

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class excel_semicolon(csv.excel):
    delimiter = ';'
    quoting = csv.QUOTE_NONNUMERIC

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
    self.pd_authors = 'AF'
    self.pd_affiliation = 'C1'
    self.pd_year = 'PY'

    self.df_rel = list()
    self.df_author = list()
    
  def match(self, query=''):
    result = [name for name in self.generate_abbreviations(query) if self.coauthors.has_node(name)]

    if len(result) == 0:
      return query
    else:
      return result[0]

  def load_csv(self):
    if os.path.exists('rels.pickle') and os.path.exists('author.pickle'):
      logging.info("Carregando lista de autores e relacionamentos do cache")
      with open('rels.pickle', 'rb') as rels_file:
        self.df_rel = pickle.load(rels_file)
      with open('authors.pickle', 'rb') as authors_file:
        self.df_author = pickle.load(authors_file)
      return

    logging.debug(
      "Carregando os seguintes arquivos "+str(glob.glob(os.path.join('data', "savedrecs-3*.txt")))
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
        glob.glob(os.path.join('data', "savedrecs-3*.txt"))
        )
      )      
      
    logging.debug(f"DataFrame shape: {df.shape}")

    logging.debug("Resolvendo filiações")
    affiliations = WoS.resolv_affiliation(df, self.pd_affiliation)

    logging.debug("Criando índice de apelidos")
    aliases_index = WoS.create_aliases_index()

    logging.debug("Processando autoria de publicações")
    df_publications = df[[self.pd_authors, self.pd_year]]
    del df

    author_dict = {}
    rels = list()
    author_idx = 1
    for row in df_publications.values:
      pub_year = 0  
      try:
        pub_year = int(row[1])
      except ValueError:
        pub_year = 1950
      
      authors = list(map(str.strip, row[0].split(';'))) 
      start = pub_year
      stop = pub_year       
        
      for author in authors:
        if author not in author_dict.keys():
          author_dict[author] = author_idx
          author_idx += 1

        current_author = author_dict[author]
        author_label = aliases_index.get(author, author)


        if author_label != author:
          logging.debug("Match de alias !!!")
        try:
          aff = affiliations[author]
          if aff.find('Univ Brasilia') >=0:
            self.df_author.append(
              {'Id':current_author,
              'Label': author,
              'also_known_as': list(), 
                'start':start,
                'stop':stop,
                'affiliation':aff,
                'color': '#00FF00'}
                )
          else:
            self.df_author.append(
              {'Id':current_author,
              'Label': author, 
              'also_known_as': list(),
                'start':start,
                'stop':stop,
                'affiliation':aff,
                'color': '#0000FF'}
                )
        except KeyError:
          self.df_author.append(
              {'Id':current_author,
              'Label': author, 
              'also_known_as': list(),
                'start':start,
                'stop':stop,
                'affiliation':'',
                'color': '#000000'}
                )

      for author in authors:
        for v in authors:
          if author != v:
            self.df_rel.append({'source':author_dict[author], 'target': author_dict[v], 'Time Interval': [start, stop]})
    with open('rels.pickle', 'wb') as rels_file:
      pickle.dump(self.df_rel, rels_file)
    with open('authors.pickle', 'wb') as authors_file:
      pickle.dump(self.df_author, authors_file)

  @timeit
  def consolidate_authors(self):
    logging.debug("Consolidating authors ...")
    for author in self.df_author:
      for author_inner in self.df_author:
        if (self.comparacao_compacta(author['Label'], author_inner['Label'])):
          author['also_known_as'].append(author_inner['Label'])
          if author_inner['start'] < author['start']:
            author['start'] = author_inner['start']
          if author_inner['stop'] > author['stop']:
            author['stop'] = author_inner['stop']
          self.df_author.remove(author_inner)
    
    logging.debug("Updating relationships")
    #Atualiza o nome do autores nos relacionamentos
    for rel in self.df_rel:
      for author in self.df_author:
        if rel['source'] in author['also_known_as']:
          rel['source'] = author['Id']
        if rel['target'] in author['also_known_as']:
          rel['target'] = author['Id']

  @timeit
  def save_to_csv(self):
    with open("data\\wos-author.csv", 'w', encoding='utf-8-sig', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=['Id','Label','Time Interval','affiliation','color'], dialect=excel_semicolon)
      writer.writeheader()
      for row in self.df_author:
        writer.writerow({'Id': row['Id'],
          'Label': row['Label'],
          'Time Interval': f'<{row["start"],row["stop"]}>',
          'affiliation': row['affiliation'],
          'color': row['color']
        })

    with open("data\\wos-rels.csv", 'w', encoding='utf-8-sig', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=['Source', 'Target', 'Time Interval'], dialect=excel_semicolon)
      writer.writeheader()
      for row in self.df_rel:
        writer.writerow(
          {'Source': row['source'],
          'Target': row['target'],
          'Time Interval': f"<[{row['Time Interval'][0]},{row['Time Interval'][1]}]>"
          }
        )


  @timeit
  def save_df_to_csv(self):
    self.df_rel.to_csv("data\\wos-rels.csv", index=False, sep=';')
    self.df_author.to_csv("data\\wos-author.csv", index=False, sep=';')
            
  @timeit  
  def write_gexf(self, outfile="data\\wos.gexf", version='1.2draft'):
    logging.debug(f"Salvando rede social no arquivo: {outfile}")
    raise NotImplementedError("Ainda não é possivel salvar o arquivo")

  def generate_abbreviations(self, name):
    '''
    @description: Gera as possíveis abreviações usadas por um autor para o nome de citacao
    '''
    if name.find('.') > 0:
      return
    name = name.strip()
    surname = ''
    first_name = ''
    try:
      surname, first_name, = name.split(',')
    except ValueError:
      print("Tentativa de dividir ", name)
      first_name = name[:name.find(' ')]
      surname = name[name.find(' ')+1:]
     
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
  def comparacao_compacta(nome1: str, nome2: str) -> bool:
    translation = {' ': None, '.': None}
    nome1 = nome1.translate(translation)
    nome2 = nome2.translate(translation)

    tokens1 = nome1.split(',')
    tokens2 = nome2.split(',')

    if tokens1[0] != tokens2[0]:
        return False
    if "".join(filter(str.isupper, [c for s in tokens1[1:] for c in s])) == "".join(filter(str.isupper, [c for s in tokens2[1:] for c in s])):
        return True
    return False
        
     
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
