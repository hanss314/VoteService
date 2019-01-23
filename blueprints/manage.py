import time
import csv
import json

from datetime import datetime
from io import StringIO

from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware

from asyncpg.exceptions import UniqueViolationError
from .oauth import make_session, API_URL, oauth_middleware
from .utils.database import conn
from config import debug, session_key

manage_bp = Starlette(debug=debug)


CACHE_RESCAN_PERIOD = 300
CACHE_CLEAR_PERIOD = 3000
last_clear = time.time()

guild_cache = {}

def guild_owner(f):
    async def wrapper(request):
        gid = request.path_params.get('gid', None)
        if gid is None: return Response("", 404)
        guilds = all_guilds(request.session)
        guilds = {g['id']: g for g in guilds}
        if gid not in guilds: return Response("", 403)
        if not guilds[gid]['permissions'] & 32:
            return Response("", 400)

        return await f(request)

    wrapper.__name__ = f.__name__
    return wrapper

manage_bp.add_middleware(SessionMiddleware, secret_key=session_key)

def all_guilds(session):
    key = session.get('key', None)
    now = time.time()
    if last_clear + CACHE_CLEAR_PERIOD < now:
        guild_cache.clear()

    if key in guild_cache and \
            session.get('last_guild_check', 0) + CACHE_RESCAN_PERIOD > now:
        return guild_cache[key]

    token = session.get('oauth2_token')
    discord = make_session(session, token=token)
    guilds = discord.get(API_URL + '/users/@me/guilds').json()
    guild_cache[key] = guilds
    session['last_guild_check'] = now
    # print(guilds)
    return guilds


@manage_bp.route('/', methods=['PUT'])
@oauth_middleware
@guild_owner
async def add_guilds(request):
    gid = request.path_params.get('gid', None)
    if gid is None: return Response('', 404)
    guilds = all_guilds(request.session)
    print(guilds)
    guilds = {g['id']: g for g in guilds}
    if gid not in guilds: return Response('', 403)
    if not guilds[gid]['permissions'] & 32:
        return Response("", 400)

    try:
        status = await conn.execute(
            'INSERT INTO guilds (id, deadline) VALUES ($1, $2)',
            gid, datetime.utcnow()
        )
    except UniqueViolationError:
        return PlainTextResponse("Guild already added", 400)

    print(status)
    return JSONResponse({'gid': gid})


@manage_bp.route('/responses', methods=['GET'])
@oauth_middleware
@guild_owner
async def get_responses(request):
    gid = request.path_params.get('gid', None)
    data = await conn.fetch(
        'SELECT ind, author, content FROM responses WHERE guild=$1', gid
    )
    return JSONResponse([dict(r) for r in data])

@manage_bp.route('/responses/{ind}', methods=['GET'])
#@oauth_middleware
#@guild_owner
async def get_responses(request):
    gid = request.path_params.get('gid', None)
    ind = request.path_params.get('ind', None)
    try:
        ind = int(ind)
    except ValueError:
        return Response('', 404)

    data = await conn.fetchrow(
        '''SELECT ind, author, content FROM responses 
           WHERE guild=$1 AND ind=$2''', gid, ind
    )
    if data is None: return Response('', 404)
    return JSONResponse(dict(data))

@manage_bp.route('/responses/upload', methods=['POST'])
@oauth_middleware
@guild_owner
async def add_response_file(request):
    form = await request.form()
    if 'file' not in form:
        return Response('No file submitted', 400)

    file = form['file']
    if not file.filename: return Response('No file submitted', 400)
    if not file.filename.endswith('.csv'):
        return Response('Not a CSV file', 400)

    file_content = StringIO((await file.read()).decode('utf-8'))
    gid = request.path_params.get('gid', None)
    csvfile = csv.reader(file_content)
    ind = await conn.fetchval(
        'SELECT MAX(guild) FROM responses WHERE guild=$1', gid
    )
    ind += 1
    count = 0
    for row in csvfile:
        await conn.execute("""
            INSERT INTO responses (guild, ind, author, content)
            VALUES ($1, $2, $3, $4)
            """, gid, ind+count, row[0], row[1]
        )
        count += 1

    return PlainTextResponse(str(count))

@manage_bp.route('/responses/{id:int}', methods=['DELETE'])
@oauth_middleware
@guild_owner
async def delete_response(request):
    gid = request.path_params.get('gid', None)
    rid = request.path_params.get('id')
    count = await conn.execute("""
        DELETE FROM responses
        WHERE guild=$1 AND ind=$2
        """, gid, rid
    )
    return Response(count.replace('DELETE ', ''), 200)

@manage_bp.route('/responses/{id:int}', methods=['PATCH'])
@oauth_middleware
@guild_owner
async def edit_response(request):
    gid = request.path_params.get('gid', None)
    rid = request.path_params.get('id')
    data = await request.json()

    response = None
    if 'author' in data:
        response = await conn.fetchrow("""
            UPDATE responses SET author=$3
            WHERE guild=$1 AND ind=$2
            RETURNING *
            """, gid, rid, data['author']
        )

    if 'content' in data:
        response = await conn.fetchrow("""
            UPDATE responses SET content=$3
            WHERE guild=$1 AND ind=$2
            RETURNING *
            """, gid, rid, data['content']
         )
    if response is None:
        return PlainTextResponse("Please select a valid field to edit", 400)

    return JSONResponse(dict(response))

@manage_bp.route('/responses', methods=['POST'])
@oauth_middleware
@guild_owner
async def add_response(request):
    data = await request.json()
    gid = request.path_params.get('gid', None)
    author = data.get('author', '')
    content = data.get('content', '')
    ind = await conn.fetchval(
        'SELECT MAX(ind) FROM responses WHERE guild=$1', gid
    )
    await conn.execute("""
        INSERT INTO responses (guild, ind, author, content)
        VALUES ($1, $2, $3, $4)
        """, gid, ind+1, author, content
    )

    response = {'gid': gid, 'ind': ind, 'author': author, 'content': content}
    return JSONResponse(response)
