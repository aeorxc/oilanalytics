import requests


def get_token(username, password):
    url = "https://www.jodidata.org/api/token"
    myobj = {"username": username, "password": password}

    x = requests.post(url, data=myobj)

    return x.text
