from flask import Flask, request, render_template
from werkzeug.exceptions import abort

# Declaring a Flask app
app = Flask(__name__)

# setting config
app.config['UPLOAD_FOLDER'] = 'uploads'


# routes

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
@app.route("/login/<string:username>", methods=['GET', 'POST'])
def login():
    return 'login'


@app.route("/register", methods=['GET', 'POST'])
@app.route("/register/<string:username>", methods=['GET', 'POST'])
def register():
    return 'register'


@app.route("/apply/", methods=['GET', 'POST'])
@app.route("/apply/<int:user_id>", methods=['GET', 'POST'])
def apply():
    return 'apply'


@app.route("/recruit", methods=['GET', 'POST'])
@app.route("/recruit/<int:recruition_id>", methods=['GET', 'POST'])
def recruit():
    return 'recruit'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
