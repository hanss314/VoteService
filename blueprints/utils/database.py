import psycopg2
import atexit
from ruamel import yaml

with open('config/creds.yml', 'r') as creds_file:
    creds = yaml.safe_load(creds_file)

with open('config/config.yml', 'r') as cfg_file:
    config = yaml.safe_load(cfg_file)

conn = psycopg2.connect(
    f"dbname={config['pgdb']} "
    f"user={config['pguser']} "
    f"host={config['pghost']} "
    f"password={creds['pgpass']}"
)

@atexit.register
def goodbye():
    conn.close()