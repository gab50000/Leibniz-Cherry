import os
import time
import tempfile

import cherrypy
from cherrypy.lib import static


class Test:
    @cherrypy.expose
    def index(self):
        return '<META http-equiv="refresh" content="5;URL=/hello">'

    @cherrypy.expose
    def hello(self):
        return "Hello"

    @cherrypy.expose
    def fup(self):
        return """
        <html><body>
            <h2>Upload a file</h2>
            <form action="upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="my_file" /><br />
            <input type="submit" />
            </form>
            <h2>Download a file</h2>
            <a href='download'>This one</a>
        </body></html>
        """

    @cherrypy.expose
    def upload(self, my_file):
        with open(os.path.join(PATH, "files", my_file.filename), "wb") as f:
            while True:
                data = my_file.file.read(8192)
                if not data:
                    break
                f.write(data)
        return '<META http-equiv="refresh" content="1;URL=/download?filename={}">'.format(my_file.filename)

    @cherrypy.expose
    def download(self, filename):
        filepath = os.path.join(PATH, "files", filename)
        return static.serve_file(filepath, "application/x-download", "attachment", 
                                os.path.basename(filepath))


if __name__ == "__main__":
    cherrypy.quickstart(Test())
