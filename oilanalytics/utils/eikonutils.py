import os

import eikon as ek


def setup_eikon():
    try:
        eikonkey = os.environ["EIKON_KEY"]

    except KeyError:
        eikonkey = ""

    ek.set_app_key(eikonkey)
