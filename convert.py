import logging
import os
import time
import tempfile
from io import BytesIO
from zipfile import ZipFile
import subprocess
import configparser
from conf import PLASTEX_PATH

import cherrypy
from cherrypy.lib import static

from show_tests import Tests


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


cf = configparser.ConfigParser()
cf.read("auth")
USER = cf["auth"]["user"]
PASS = cf["auth"]["password"]


SUBMIT_FORM = """
<html><body>
    <h2>Zip-File auswählen:</h2>
    <p> (Latex-Datei mit allen Unterdateien muss in dem gezippten Ordner liegen) </p>
    <form action="upload" method="post" enctype="multipart/form-data">
    <input type="file" name="my_file" /><br />
    <input type="submit" />
    </form>
</body></html>
"""


def unpack(source_file, dest_dir):
    zf = ZipFile(source_file)
    zf.extractall(dest_dir)


def process(dir_name):
    contained_files = [os.path.join(dir_name, x) for x in os.listdir(dir_name)]
    for x in contained_files:
        logger.debug(f"Checking {x}")
        if os.path.isfile(x) and x.endswith(".tex"):
            logger.debug(f"Found file {x}")
            subprocess.check_call([PLASTEX_PATH, x])
            return x[:-4] + ".xml"
    else:
        logger.debug("Found no tex file")
        if len(contained_files) == 1:
            if os.path.isdir(contained_files[0]):
                logger.debug(f"Found only one directory {contained_files[0]}")
                return process(os.path.join(dir_name, contained_files[0]))


def authenticate(realm, user, password):
    return user == USER and password == PASS


class Main:
    @cherrypy.expose
    def index(self):
        return SUBMIT_FORM

    @cherrypy.expose
    def upload(self, my_file):
        if not my_file.filename.endswith(".zip"):
            return """
            <p>Bitte eine Zip-Datei hochladen</p>
            <a href="/index">Zurück</a>
            """

        buf = BytesIO()
        while True:
            data = my_file.file.read(8192)
            if not data:
                break
            buf.write(data)
        buf.seek(0)
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger.debug(f"Temporary file {tmp_dir} created")
            unpack(buf, tmp_dir)
            result = process(tmp_dir)
            if result:
                logger.debug(f"Result file: {result}")
                return static.serve_file(os.path.join(tmp_dir, result), "application/x-download",
                                         "attachment", result)
            else:
                return "<b> Keine Tex-Datei gefunden! </b>"


if __name__ == "__main__":
    cherrypy.tree.mount(Main(), "/", "cherry.cfg")
    cherrypy.quickstart(Tests(), "/tests", "cherry.cfg")