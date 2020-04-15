from dpidpo.scopus import Scopus
from dpidpo.wos import WoS

def main():
    #scopus = Scopus()
    wos = WoS()

    #print(scopus.search("Dalton Martins"))
    #scopus.load_csv()
    print(" *** Loading data ***")
    wos.load_csv()

    print(" *** Generating graph file ***")
    wos.write_gexf()


if __name__ == "__main__":
    main()