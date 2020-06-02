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
  def __init__(self, filtro_de_ano = list()):
    self.pd_authors = 'AF'
    self.pd_affiliation = 'C1'
    self.pd_year = 'PY'

    self.filtro_de_ano = filtro_de_ano if len(filtro_de_ano) == 2 else Exception("Erro ao configurar o filtro de anos")
    self.df_rel = dict()
    self.df_author = dict()
    
  def match(self, query=''):
    result = [name for name in self.generate_abbreviations(query) if self.coauthors.has_node(name)]

    if len(result) == 0:
      return query
    else:
      return result[0]

  def load_csv(self):
    files_suffix = f"{self.filtro_de_ano[0]}-{self.filtro_de_ano[1]}"
    if os.path.exists(f'rels-{files_suffix}.pickle') and os.path.exists(f'author-{files_suffix}.pickle'):
      logging.info("Carregando lista de autores e relacionamentos do cache")
      with open(f'rels-{files_suffix}.pickle', 'rb') as rels_file:
        self.df_rel = pickle.load(rels_file)
      with open(f'authors-{files_suffix}.pickle', 'rb') as authors_file:
        self.df_author = pickle.load(authors_file)
      return

    logging.debug(
      "Carregando os seguintes arquivos "+str(glob.glob(os.path.join('data', "savedrecs-*.txt")))
      )
    df_raw = pd.concat(
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

    filter_years = list(range(int(self.filtro_de_ano[0]), int(self.filtro_de_ano[1])))
    
    logging.debug(f"Raw DataFrame shape: {df_raw.shape}")

    logging.debug(f"Filtrando publicações para os anos {filter_years}")
    
    df = df_raw[pd.to_numeric(df_raw.PY, downcast='integer').isin(filter_years)]
    del df_raw

    logging.debug(f"DataFrame shape: {df.shape}")

    logging.debug("Resolvendo filiações")
    affiliations = WoS.resolv_affiliation(df, self.pd_affiliation)

    logging.debug("Criando índice de apelidos")
    aliases_index = WoS.create_aliases_index()

    logging.debug("Processando autoria de publicações")
    df_publications = df[[self.pd_authors, self.pd_year]]
    del df

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
        if author not in self.df_author.keys():
          self.df_author[author] = {
            'Id': author_idx, 
            'Label': author,
            'also_known_as': aliases_index.get(author, list()),
            'start':start,
            'stop':stop,
            'affiliation':affiliations.get(author, None)
            }
          author_idx += 1
        else:
          current_author = self.df_author[author]

          if current_author['start'] > start:
            current_author['start'] = start
          if current_author['stop'] < stop:
            current_author['stop'] = stop
          if current_author['affiliation'] is None:
            current_author['affiliation'] = affiliations.get(author, None)

          self.df_author[author] = current_author
                
      for author in authors:
        for v in authors:
          if author != v:
            key = f"{author}{v}"
            if key not in self.df_rel.keys():
              self.df_rel[key] = {
              'source':self.df_author[author]['Id'], 
              'target': self.df_author[v]['Id'], 
              'Time Interval': [(start, stop)]
              }
            else:
              self.df_rel[key]['Time Interval'].append((start, stop))

    # Serializa as listas de autores e relacionamentos
    with open(f'rels-{files_suffix}.pickle', 'wb') as rels_file:
      pickle.dump(self.df_rel, rels_file)
    with open(f'authors-{files_suffix}.pickle', 'wb') as authors_file:
      pickle.dump(self.df_author, authors_file)

  @timeit
  def consolidate_authors(self):
    logging.debug("Consolidando autores ...")
    for author in self.df_author.keys():
      sinonimos = list()
      for author_inner in self.df_author.keys():
        if (self.comparacao_compacta(author, author_inner)):
          sinonimos.append(self.df_author[author_inner])
      if len(sinonimos) == 0:
        continue
      start = min([x['start'] for x in sinonimos])
      stop = max([x['stop'] for x in sinonimos])
      mantem = max(sinonimos, key=lambda x:len(x['Label']))

      self.df_author[mantem['Label']]['start']=start
      self.df_author[mantem['Label']]['stop']=stop
      sinonimos.remove(mantem)
      map(lambda x: self.df_author[x['Label']], sinonimos)

      for rel_key in self.df_rel.keys():
        if self.df_rel[rel_key]['source'] in [x['Id'] for x in sinonimos]:
          self.df_rel[rel_key]['source'] = mantem['Id']
        if self.df_rel[rel_key]['target'] in [x['Id'] for x in sinonimos]:
          self.df_rel[rel_key]['target'] = mantem['Id']

  @timeit
  def save_to_csv(self):
    files_suffix = f"{self.filtro_de_ano[0]}-{self.filtro_de_ano[1]}"
    with open(f"data\\wos-author-{files_suffix}.csv", 'w', encoding='utf-8-sig', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=['Id','Label','Time Interval','affiliation','also_known_as'], dialect=excel_semicolon)
      writer.writeheader()
      for key,row in self.df_author.items():
        writer.writerow({'Id': row['Id'],
          'Label': row['Label'],
          'Time Interval': f'<[{row["start"]},{row["stop"]}]>',
          'affiliation': row['affiliation'],
          'also_known_as': row['also_known_as']
        })

    with open(f"data\\wos-rels-{files_suffix}.csv", 'w', encoding='utf-8-sig', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=['Source', 'Target', 'Time Interval'], dialect=excel_semicolon)
      writer.writeheader()
      for key,row in self.df_rel.items():
        writer.writerow(
          {'Source': row['source'],
          'Target': row['target'],
          'Time Interval': "<"+";".join([str(list(x)) for x in row['Time Interval']])+">"
          }
        )

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
