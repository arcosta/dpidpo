from dpidpo import __version__

from dpidpo.wos import WoS
import os

def test_version():
    assert __version__ == '0.1.0'

def test_load_wos():
    repo = WoS()
    repo.load_csv()

def test_search():
    repo = WoS()
    assert repo.search("Fulano") is not None

def test_write_gexf():
    repo = WoS()
    outfile = os.path.join("data","test.gexf")
    repo.write_gexf(outfile=outfile)
    assert os.path.isfile(outfile) is True

def test_generate_abbreviations():
    wos = WoS()
    for i in wos.generate_abbreviations(name="Ralha, Celia Ghedini"):
        print(i)
