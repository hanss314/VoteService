import asyncpg
from ruamel import yaml

with open('config/creds.yml', 'r') as creds_file:
    creds = yaml.safe_load(creds_file)

with open('config/config.yml', 'r') as cfg_file:
    config = yaml.safe_load(cfg_file)

class Pool:
    def __init__(self):
        self.c = None

    async def start(self):
        self.c = await asyncpg.create_pool(
            database=config['pgdb'],
            user=config['pguser'],
            host=config['pghost'],
            password=creds['pgpass']
        )

    async def stop(self):
        await self.c.close()
    """
    def execute(self, *args, **kwargs):
        return self.c.execute(*args, **kwargs)

    def fetch(self, *args, **kwargs):
        return self.c.fetch(*args, **kwargs)

    def fetchrow(self, *args, **kwargs):
        return self.c.fetchrow(*args, **kwargs)

    def fetchval(self, *args, **kwargs):
        return self.c.fetchval(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self.c.executemany(*args, **kwargs)
    
    def transaction(self, *args, **kwargs):
        return self.c.transaction(*args, **kwargs)

    def cursor(self, *args, **kwargs):
        return self.c.cursor(*args, **kwargs)

    def prepare(self, *args, **kwargs):
        return self.c.prepare(*args, **kwargs)
        """
    def acquire(self, *args, **kwargs):
        return self.c.acquire(*args, **kwargs)

    def release(self, *args, **kwargs):
        return self.c.release(*args, **kwargs)




pool = Pool()
