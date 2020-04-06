from dpidpo import __version__

from dpidpo.wos import WoS

def test_version():
    assert __version__ == '0.1.0'

def teste_load_wos():
    repo = WoS()
    repo.load_csv()
