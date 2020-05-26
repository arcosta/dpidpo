#from dpidpo.scopus import Scopus
from dpidpo.wos import WoS
from datetime import datetime

def main():
    start_time = datetime.now()
    #scopus = Scopus()
    wos = WoS()

    #print(scopus.search("Dalton Martins"))
    #scopus.load_csv()
    print(" *** Loading data ***")
    wos.load_csv()

    #wos.consolidate_authors()

    print(" *** Generating graph file ***")
    #wos.write_gexf()
    wos.save_to_csv()

    final_time = datetime.now()

    print("Time elapsed: ", final_time - start_time)


if __name__ == "__main__":
    main()