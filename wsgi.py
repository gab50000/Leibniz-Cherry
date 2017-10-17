import sys
sys.stdout = sys.stderr

import atexit
import cherrypy

from main import Main
from convert import Convert
from show_tests import Tests

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

class Root(object):
    def index(self):
        return 'Hello World!'
    index.exposed = True

application = cherrypy.Application(Main(), script_name='', config=None)
                                   cherrypy.tree.mount(Convert(), "/convert", config_path)
                                   cherrypy.quickstart(Tests(), "/tests", config_path)
