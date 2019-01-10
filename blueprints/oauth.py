import os

from ruamel import yaml
from requests_oauthlib import OAuth2Session
from flask import session, redirect, Blueprint, request

with open('config/creds.yml', 'r') as creds_file:
    creds = yaml.safe_load(creds_file)

with open('config/config.yml', 'r') as cfg_file:
    config = yaml.safe_load(cfg_file)

REDIRECT = config['redirect']
OAUTH2_CLIENT_ID = config['appid']
OAUTH2_CLIENT_SECRET = creds['appsecret']

API_URL = 'https://discordapp.com/api'

if 'http://' in REDIRECT:
    secure = False
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
else:
    secure = True

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth2')

def make_session(token=None, state=None, scope=None):
    def token_updater(t):
        session['oauth2_token'] = t

    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=API_URL+'/oauth2/token',
        token_updater=token_updater
    )

def auth_required(f):
    def wrapper(*args, **kwargs):
        if 'key' not in session:
            discord = make_session(scope='identify guilds')
            authorization_url, state = discord.authorization_url(API_URL+'/oauth2/authorize')
            session['oauth2_state'] = state
            return redirect(authorization_url, code=312)

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


@oauth_bp.route('', methods=['GET'])
def oauth2_complete():
    discord = make_session(state=session.get('oauth2_state'))
    session['oauth2_token'] = discord.fetch_token(
        API_URL+'/oauth2/token',
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url
    )
    user = discord.get(API_URL + '/users/@me').json()
    session['key'] = request.args.get('code')
    session['uid'] = user['id']
    return redirect(session.get('oauth2_redirect', '/'))

@oauth_bp.route('/save', methods=['POST'])
def oauth2_save():
    session['oauth2_redirect'] = request.json.get('location', '')
    return '', 200