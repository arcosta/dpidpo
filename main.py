from dpidpo.scopus import Scopus

def main():
    scopus = Scopus()

    print(scopus.search("Dalton Martins"))


if __name__ == "__main__":
    main()