import logging
import os
import textwrap

import cherrypy
from cherrypy.lib import static

from conf import TEST_PATH
from helpers import HTMLList, HTMLLink


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


test_page_content = """
<h2> Inhalt von {name} </h2>
<pre>
{tex_content}
</pre>

{link}"""

def show_test_factory(name):
    def show_test():
        dir_ = os.path.join(TEST_PATH, name)
        latex_files = [f for f in os.listdir(dir_) if f.endswith(".tex")]
        logger.debug(f"Looking what's inside of {dir_}")
        if latex_files:
            with open(os.path.join(dir_, latex_files[0]), "r") as f:
                tex_content = f.read()
        else:
            tex_content = ""
        return test_page_content.format(name=name, tex_content=tex_content,
                                        link=HTMLLink("Zurück", "./"))
    return show_test


class Tests:
    def __init__(self):
        test_content = [x for x in os.listdir(TEST_PATH)
                        if os.path.isdir(os.path.join(TEST_PATH, x))]
        logger.debug(f"Found tests {test_content}")

        for test in test_content:
            setattr(self, test, cherrypy.expose(show_test_factory(test)))

    @cherrypy.expose
    def index(self):
        tests = [HTMLLink(x, f"{x}") for x in dir(self)
                 if callable(getattr(self, x)) and not x.startswith("_") and not x == "index"]
        return f""" <h2> Verfügbare Tests: </h2>
        {str(HTMLList(tests))}"""


if __name__ == "__main__":
    cherrypy.config.update("cherry.cfg")
    cherrypy.quickstart(Tests(), "/", "cherry.cfg")
