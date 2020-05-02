from dpidpo.scopus import Scopus
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

    print(" *** Generating graph file ***")
    wos.write_gexf()

    final_time = datetime.now()

    print("Time elapsed: ", final_time - start_time)


if __name__ == "__main__":
    main()