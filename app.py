import os

from flask import Flask, session, request, redirect, jsonify, render_template
from blueprints.oauth import oauth_bp
from blueprints.api import api_bp

app = Flask(__name__)

app.secret_key = os.urandom(16)
app.config['SESSION_TYPE'] = 'filesystem'
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.register_blueprint(oauth_bp)
app.register_blueprint(api_bp)


@app.route('/', defaults={'_': ''})
@app.route('/<path:_>')
def index(_):
    return render_template('index.html')


if __name__ == '__main__':
    host = '0.0.0.0'
    port = os.environ.get('PORT', 3000)
    app.debug = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(host=host, port=port)

