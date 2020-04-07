import pandas as pd
import networkx as nx
import glob
import os

class WoS(object):
  def __init__(self):
    self.coauthors = nx.Graph()

  def search(self, query=''):
    pass

  def load_csv(self):
    df = pd.concat(
      map(
        lambda file: pd.read_csv(file, sep='\t+', header=0, encoding='utf-8-sig'), 
        glob.glob(os.path.join('data', "savedrecs-4*.txt"))
        )
        )

    affiliations = WoS.resolv_affiliation(df, "SE")

    for row in df[['BA', 'CR']].values:
        authors = list(map(str.strip, row[0].split(';')))
        
        try:
          pub_year = int(row[1])
        except ValueError:
          pub_year = 1059
        for author in authors:
          try:
            aff = affiliations[author]
            if aff.find('Univ Brasilia') >=0:
              self.coauthors.add_node(author, affiliation=aff, color='#00FF00')
            else:
              self.coauthors.add_node(author, affiliation=aff)
          except KeyError:
            self.coauthors.add_node(author)

        for u in authors:
          for v in authors:
            if u != v:
              self.coauthors.add_edge(u, v, start=pub_year, stop=2021)

    
  def write_gexf(self, outfile="data\\wos.gexf"):
    nx.write_gexf(self.coauthors, outfile)

  @staticmethod
  def resolv_affiliation(df, column_aff):
    '''
    @description: Extract the affiliation data of authors
    @return: A dict with authors name as keys
    '''
    result = {}
    for row in df[column_aff]:
      if row.find('[') < 0:
        for author_address in row.split(';'):
          name = ''.join(author_address.split(',')[:2]).replace(' (reprint author)', '')
          address = ''.join(author_address.split(',')[2:]).strip()
          result[name] = address
      else:
        authors_addr = row.split('; [')
        for inner_author_addr in authors_addr:
          authors,addr = inner_author_addr.split('] ')
          for author in authors.split(';'):
            result[author] = addr

    return result


  
