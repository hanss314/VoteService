import uvicorn

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from config import debug
from blueprints.guilds import guilds_bp
from blueprints.oauth import oauth_bp
from blueprints.manage import manage_bp
from blueprints.utils.database import pool


app = Starlette(debug=debug, template_directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

#app.secret_key = os.urandom(16)
# app.config['SESSION_TYPE'] = 'filesystem'
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.mount('/api/guilds', guilds_bp, name='guilds')
app.mount('/api/{gid}', manage_bp, name='manage')
app.mount('/oauth2', oauth_bp, name='oauth')


@app.route('/')
@app.route('/{p:path}')
def index(request):
    template = app.get_template('index.html')
    content = template.render(request=request)
    return HTMLResponse(content)

@app.on_event('startup')
async def create_db_connection():
    await pool.start()

@app.on_event('shutdown')
async def close_db_connection():
    await pool.stop()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000)

