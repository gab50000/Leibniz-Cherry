import logging
import os

import cherrypy
from cherrypy.lib import static

from conf import TEST_PATH
from helpers import HTMLList


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def show_test_factory(name):
    def show_test():
        dir_ = os.path.join(TEST_PATH, name)
        logger.debug(f"Looking what's inside of {dir_}")
        return f"""<h2> Inhalt von {name} </h2>
        {str(HTMLList(os.listdir(dir_)))}"""
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
        return "Hello"


if __name__ == "__main__":
    cherrypy.config.update("cherry.cfg")
    cherrypy.quickstart(Tests(), "/", "cherry.cfg")
