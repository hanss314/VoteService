import psycopg2
import time
import csv

from datetime import datetime
from io import StringIO
from flask import session, Blueprint, request, jsonify, abort
from .oauth import auth_required, make_session, API_URL
from .utils.database import conn

api_bp = Blueprint('api', __name__, url_prefix='/api')

CACHE_RESCAN_PERIOD = 300
CACHE_CLEAR_PERIOD = 3000
last_clear = time.time()

guild_cache = {}

def all_guilds():
    key = session.get('key', None)
    now = time.time()
    if last_clear + CACHE_CLEAR_PERIOD < now:
        guild_cache.clear()

    if key in guild_cache and \
            session.get('last_guild_check', 0) + CACHE_RESCAN_PERIOD < now:
        return guild_cache[key]

    token = session.get('oauth2_token')
    discord = make_session(token=token)
    guilds = discord.get(API_URL + '/users/@me/guilds').json()
    guild_cache[key] = guilds
    session['last_guild_check'] = now
    # print(guilds)
    return guilds

def manage_server(f):
    def wrapper(*args):
        if request.json: gid = request.json.get('gid', None)
        else: gid = request.form.get('gid', None)
        if gid is None: return abort(404)
        guilds = all_guilds()
        guilds = {g['id']: g for g in guilds}
        if gid not in guilds: return abort(403)
        if not guilds[gid]['permissions'] & 32:
            return abort(400)

        return f(*args)

    wrapper.__name__ = f.__name__
    return wrapper


@api_bp.route('/guilds', methods=['GET'])
@auth_required
def get_guilds():
    return jsonify(all_guilds())


@api_bp.route('/guilds', methods=['POST'])
@auth_required
@manage_server
def add_guilds():
    gid = request.json.get('gid', None)
    if gid is None: return abort(404)
    guilds = all_guilds()
    guilds = {g['id']: g for g in guilds}
    if gid not in guilds: return abort(403)
    if not guilds[gid]['permissions'] & 32:
        return abort(400)

    with conn.cursor() as cur:
        try:
            cur.execute(
                'INSERT INTO guilds (id, deadline) VALUES (%s, %s)',
                (gid, datetime.utcnow())
            )
        except psycopg2.IntegrityError:
            return abort(400, 'Guild is already registered')
        else:
            conn.commit()

    return jsonify({'gid': gid})

@api_bp.route('/guilds/registered', methods=['GET'])
@auth_required
def get_used_guilds():
    guilds = all_guilds()
    gids = {g['id']: g for g in guilds}
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id FROM guilds WHERE id IN %s',
            (list(map(int, gids.keys())),)
        )
        guilds = [gids[i[0]] for i in cur.fetchall()]

    return jsonify(guilds)

@api_bp.route('/guilds/registered/<string:gid>', methods=['GET'])
@auth_required
def get_used_guild(gid):
    guilds = all_guilds()
    gids = {g['id']: g for g in guilds}
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id FROM guilds WHERE id = %s LIMIT 1',
            (gid,)
        )
        guilds = [gids[i[0]] for i in cur.fetchall()]

    if not guilds: return abort(404)

    return jsonify(guilds[0])

@api_bp.route('/responses', methods=['POST'])
@auth_required
@manage_server
def add_response():
    data = request.json
    gid = data.get('gid')
    author = data.get('author', '')
    content = data.get('content', '')
    with conn.cursor() as cur:
        cur.execute(
            'SELECT COUNT(guild) FROM responses WHERE guild=%s', (gid,)
        )
        ind = cur.fetchone()
        cur.execute("""
            INSERT INTO responses (guild, ind, author, content)
            VALUES (%s, %s, %s, %s)
            """, (gid, ind[0], author, content)
        )
        conn.commit()

    response = {'gid': gid, 'ind': ind, 'author': author, 'content': content}
    return jsonify(response)

@api_bp.route('/responses/upload', methods=['POST'])
@auth_required
@manage_server
def add_response_file():
    if 'file' not in request.files:
        return abort(400, 'No file part')

    file = request.files['file']
    if not file.filename: return abort(400, 'No file selected')
    if file.mimetype != 'text/csv':
        return abort(400, 'Only CSV files are permitted')

    file_content = StringIO(file.read().decode('utf-8'))
    gid = request.form.get('gid')
    csvfile = csv.reader(file_content)
    with conn.cursor() as cur:
        cur.execute(
            'SELECT COUNT(guild) FROM responses WHERE guild=%s', (gid,)
        )
        ind = cur.fetchone()[0]
        count = 0
        for row in csvfile:
            cur.execute("""
                INSERT INTO responses (guild, ind, author, content)
                VALUES (%s, %s, %s, %s)
                """, (gid, ind+count, row[0], row[1])
            )
            count += 1

        conn.commit()

    return str(count), 200

