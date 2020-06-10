#from dpidpo.scopus import Scopus
from dpidpo.wos import WoS
from datetime import datetime
import argparse

def main():
    start_time = datetime.now()

    parser = argparse.ArgumentParser(
        description="Processa os CSV da Web of Science para gerar a rede de coautoria"
        )
    parser.add_argument('years', metavar='N', nargs='+',
                    help='Anos para o filtro de publicações')
    args = parser.parse_args()
    #scopus = Scopus()
    wos = WoS(args.years)

    #print(scopus.search("Dalton Martins"))
    #scopus.load_csv()
    print(" *** Loading data ***")
    wos.load_csv()

    wos.consolidate_authors()

    print(" *** Generating graph file ***")
    #wos.write_gexf()
    wos.save_to_csv()

    final_time = datetime.now()

    print("Time elapsed: ", final_time - start_time)


if __name__ == "__main__":
    main()