import asyncpg
from ruamel import yaml

with open('config/creds.yml', 'r') as creds_file:
    creds = yaml.safe_load(creds_file)

with open('config/config.yml', 'r') as cfg_file:
    config = yaml.safe_load(cfg_file)

class Connection:
    def __init__(self):
        self.c = None

    async def start(self):
        self.c = await asyncpg.connect(
            database=config['pgdb'],
            user=config['pguser'],
            host=config['pghost'],
            password=creds['pgpass']
        )

    async def stop(self):
        await self.c.close()

    async def execute(self, *args, **kwargs):
        return await self.c.execute(*args, **kwargs)

    async def fetch(self, *args, **kwargs):
        return await self.c.fetch(*args, **kwargs)

    async def fetchrow(self, *args, **kwargs):
        return await self.c.fetchrow(*args, **kwargs)

    async def fetchval(self, *args, **kwargs):
        return await self.c.fetchval(*args, **kwargs)

conn = Connection()
