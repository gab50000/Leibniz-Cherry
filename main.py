import logging
import os
import time
import tempfile

import cherrypy
from cherrypy.lib import static


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Test:
    @cherrypy.expose
    def hello(self):
        return "<b>Hello</b>"

    @cherrypy.expose
    def index(self):
        return """
        <html><body>
            <h2>Upload a file</h2>
            <form action="upload" method="post" enctype="multipart/form-data">
            Filename: <input type="file" name="my_file" /><br />
            <input type="submit" />
            </form>
        </body></html>
        """

    @cherrypy.expose
    def upload(self, my_file):
        if not my_file.filename.endswith(".zip"):
            return """
            <p>Bitte ein Zipfile hochladen</p>
            <a href="/index">Zurück</a>
            """

        tmpf = tempfile.NamedTemporaryFile(delete=False)
        logger.debug(f"Temporary file {tmpf.name} created")
        while True:
            data = my_file.file.read(8192)
            if not data:
                break
            tmpf.write(data)
        return '<META http-equiv="refresh" content="1;URL=/download?filename={}">'.format(tmpf.name)

    @cherrypy.expose
    def download(self, filename):
        # TODO: Delete file after download
        return static.serve_file(filename, "application/x-download", "attachment", 
                                 "result.xml")


if __name__ == "__main__":
    cherrypy.quickstart(Test())
