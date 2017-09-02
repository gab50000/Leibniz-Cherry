import logging
import os
import subprocess
from contextlib import contextmanager
import re

import cherrypy
from cherrypy.lib import static

from conf import TEST_PATH, PLASTEX_PATH
from helpers import HTMLList, HTMLLink


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


test_page_content = """
<h2> Inhalt von {name} </h2>
<h3> Tex-Datei </h3>
<pre>
{tex_content}
</pre>

<h3> XML-Datei </h3>
<pre>
{xml_content}
</pre>

{link}"""


@contextmanager
def cd(dir_):
    curdir = os.path.abspath(os.path.curdir)
    try:
        os.chdir(dir_)
        yield
    finally:
        os.chdir(curdir)


def compile_xml(dir_, filename):
    compile = False
    with cd(os.path.join(TEST_PATH, dir_)):
        if os.path.exists(filename):
            current_hash = subprocess.check_output("git rev-parse HEAD".split())\
                .decode("utf-8").strip()
            try:
                with open(filename, "r") as f:
                    text = f.readline()
                xml_hash = re.search(r"Commit Hash\:\s([a-z0-9]+)", text).group(1)
                logger.debug(f"Current Hash: {current_hash}")
                logger.debug(f"XML Hash: {xml_hash}")
                if xml_hash != current_hash:
                    logger.debug("Hashes are different. Compile")
                    compile = True
                else:
                    logger.debug("Hashes are equal. Will just read XML File")
            except AttributeError:
                logger.debug("Found no hash in XML file")
                compile = True
        else:
            compile = True

        if compile:
            subprocess.check_call([PLASTEX_PATH, filename.replace(".xml", ".tex"), "--commit"])
        with open(filename, "r") as f:
            output = f.read()
        return output


def show_test_factory(name):
    def show_test():
        dir_ = os.path.join(TEST_PATH, name)
        latex_files = [f for f in os.listdir(dir_) if f.endswith(".tex")]
        logger.debug(f"Looking what's inside of {dir_}")
        if latex_files:
            with open(os.path.join(dir_, latex_files[0]), "r") as f:
                tex_content = f.read()
            xml_content = compile_xml(dir_, latex_files[0].replace(".tex", ".xml"))
            xml_content = xml_content.replace("<", "&lt;")
            xml_content = xml_content.replace(">", "&gt;")
        else:
            tex_content = ""
            xml_content = ""
        return test_page_content.format(name=name, tex_content=tex_content, xml_content=xml_content,
                                        link=HTMLLink("Zurück", "./"))
    return show_test


class Tests:
    def __getattribute__(self, name):
        with cd(TEST_PATH):
            test_dirs = [x for x in os.listdir(".") if os.path.isdir(x)]
        logger.debug(f"Found tests {test_dirs}")
        if name in test_dirs:
            return cherrypy.expose(show_test_factory(name))
        else:
            return super().__getattribute__(name)

    @cherrypy.expose
    def index(self):
        tests = [HTMLLink(x, f"{x}") for x in os.listdir(TEST_PATH)
                 if hasattr(self, x) and not x.startswith("_")]
        return f""" <h2> Verfügbare Tests: </h2>
        {str(HTMLList(tests))}"""


if __name__ == "__main__":
    cherrypy.config.update("cherry.cfg")
    cherrypy.quickstart(Tests(), "/", "cherry.cfg")
