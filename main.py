import configparser
import os

import cherrypy

from convert import Convert
from show_tests import Tests
from helpers import HTMLLink


cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(__file__), "auth"))
USER = cf["auth"]["user"]
PASS = cf["auth"]["password"]

config_path = os.path.join(os.path.dirname(__file__), "cherry.cfg")


STARTPAGE = f"""
<h2> Latex Converter </h2>

<p> {HTMLLink("Eigenes Latex-File konvertieren", "convert")} </p>

<p> {HTMLLink("Konvertierungsbeispiele ansehen", "tests")} </p>
"""


def authenticate(realm, user, password):
    return user == USER and password == PASS


class Main:
    @cherrypy.expose
    def index(self):
        return STARTPAGE


if __name__ == "__main__":
    cherrypy.tree.mount(Main(), "/", config_path)
    cherrypy.tree.mount(Convert(), "/convert", config_path)
    cherrypy.quickstart(Tests(), "/tests", config_path)
