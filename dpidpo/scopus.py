import requests

class Scopus(object):
    def __init__(self):
        self.access_token = ''
    def search(self, query='authlast(Dalton)%20and%20authfirst(Martins)'):
        params = {
            'httpAccept': 'application/json',
            'apiKey': self.access_token,
            'query': query
        }
        response = requests.get("https://api.elsevier.com/content/search/author", params=params)

        return response.text
