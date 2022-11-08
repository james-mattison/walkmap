import flask
from flaskext.markdown import Markdown
import subprocess
import os

app = flask.Flask(__name__)
Markdown(app)

@app.route("/", methods = ["get", "post"])
def index():
    return flask.render_template("index.html")

@app.route("/img/<name>", methods = ["get"])
def img(name):
    return flask.send_from_directory("img", filename = name)

@app.route("/gather", methods = ["post", "get"])
def gather():
    os.chdir("/root")
    out = subprocess.getoutput("python3 gather.py")
    lines = out.split("\n")
    subprocess.run("python3 /var/www/html/makeindex.py", shell = True)
    return flask.redirect("http://walkmap.vixal.net/" + lines[-1].split(" ")[-1])

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 42069)
