import os

from ruamel import yaml
from requests_oauthlib import OAuth2Session

from starlette.applications import Starlette
from starlette.responses import RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware

from urllib.parse import unquote
from config import debug, session_key

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

oauth_bp = Starlette(debug=debug)


def oauth_middleware(f):
    async def wrapper(request):
        if 'key' not in request.session:
            discord = make_session(request.session, scope='identify guilds')
            authorization_url, state = discord.authorization_url(API_URL + '/oauth2/authorize')
            request.session['oauth2_state'] = state
            return RedirectResponse(unquote(authorization_url), status_code=312)

        return await f(request)

    wrapper.__name__ = f.__name__
    return wrapper


oauth_bp.add_middleware(SessionMiddleware, secret_key=session_key)


def make_session(session, token=None, state=None, scope=None):
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


@oauth_bp.route('/', methods=['GET'])
async def oauth2_complete(request):
    session = request.session
    discord = make_session(request.session, state=session.get('oauth2_state'))
    session['oauth2_token'] = discord.fetch_token(
        API_URL+'/oauth2/token',
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url._url

    )
    user = discord.get(API_URL + '/users/@me').json()
    session['key'] = request.query_params.get('code')
    session['uid'] = user['id']
    return RedirectResponse(session.get('oauth2_redirect', '/'))

@oauth_bp.route('/save', methods=['POST'])
async def oauth2_save(request):
    location = (await request.json()).get('location', '')
    request.session['oauth2_redirect'] = location
    return Response(location, 200)