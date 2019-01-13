import time

from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .oauth import OauthMiddleware, make_session, API_URL
from .utils.database import conn
from config import debug, session_key

guilds_bp = Starlette(debug=debug)
guilds_bp.add_middleware(OauthMiddleware)
guilds_bp.add_middleware(SessionMiddleware, secret_key=session_key)


CACHE_RESCAN_PERIOD = 300
CACHE_CLEAR_PERIOD = 3000
last_clear = time.time()

guild_cache = {}


def all_guilds(session):
    key = session.get('key', None)
    now = time.time()
    if last_clear + CACHE_CLEAR_PERIOD < now:
        guild_cache.clear()

    if key in guild_cache and \
            session.get('last_guild_check', 0) + CACHE_RESCAN_PERIOD < now:
        return guild_cache[key]

    token = session.get('oauth2_token')
    discord = make_session(session, token=token)
    guilds = discord.get(API_URL + '/users/@me/guilds').json()
    guild_cache[key] = guilds
    session['last_guild_check'] = now
    # print(guilds)
    return guilds

def manage_server(f):
    f.manage_guild = True
    return f

@guilds_bp.route('/', methods=['GET'])
async def get_guilds(request):
    return JSONResponse(all_guilds(request.session))


@guilds_bp.route('/registered', methods=['GET'])
async def get_used_guilds(request):
    guilds = all_guilds(request.session)
    gids = {g['id']: g for g in guilds}
    guilds = [gids[i[0]] for i in await conn.fetch(
        'SELECT id FROM guilds WHERE id IN $1',
        list(gids.keys())
    )]

    return JSONResponse(guilds)

@guilds_bp.route('/registered/{gid}', methods=['GET'])
async def get_used_guild(request):
    guilds = all_guilds(request.session)
    gids = {g['id']: g for g in guilds}
    guild = await conn.fetchval(
        'SELECT id FROM guilds WHERE id = $1 LIMIT 1',
        request.path_params['gid']
    )

    if guild is None: return Response('', 404)

    return JSONResponse(gids[guild])


