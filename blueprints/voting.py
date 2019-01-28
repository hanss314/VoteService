from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware

from .oauth import make_session, API_URL, oauth_middleware
from .manage import all_guilds
from .utils.database import pool
from config import debug, session_key

def in_guild(f):
    async def wrapper(request):
        gid = request.path_params.get('gid', None)
        if gid is None: return Response("", 404)
        guilds = all_guilds(request.session)
        guilds = {g['id']: g for g in guilds}
        if gid not in guilds: return Response("", 403)
        return await f(request)

    wrapper.__name__ = f.__name__
    return wrapper

voting_bp = Starlette(debug=debug)
voting_bp.add_middleware(SessionMiddleware, secret_key=session_key)

@voting_bp.route('/{gid}', methods=['POST'])
@oauth_middleware
@in_guild
async def start_voting(request):
    gid = request.path_params.get('gid', None)
    if gid is None: return Response('', 404)
    data = await request.json()
    try: vote = data['vote']
    except KeyError: return Response('', 400)
    session = request.session
    token = session.get('oauth2_token')
    discord = make_session(session, token=token)
    user = discord.get(API_URL + '/users/@me').json()
    uid = user['id']
    async with pool.acquire() as conn:
        canvote, length = await conn.fetchrow(
            'SELECT canvote, length FROM guilds WHERE id=$1',
            gid
        )
        if not canvote or len(vote) != length: return Response('', 400)

        await conn.execute(
            'INSERT INTO votes (guild, voter, responses) '
            'VALUES ($1, $2, $3)',
            gid, uid, vote
        )

    return JSONResponse({'gid': gid, 'uid': uid, 'vote': vote})
