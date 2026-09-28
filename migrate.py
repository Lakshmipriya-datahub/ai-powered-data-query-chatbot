import os
import re
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import create_engine, inspect, event

load_dotenv()

# Local MySQL (source)
local_pw = quote_plus(os.getenv("MYSQL_PASSWORD"))
local_engine = create_engine(
    f"mysql+mysqlconnector://root:{local_pw}@localhost/real_world_project"
)

# Aiven MySQL (destination)
aiven_pw = quote_plus(os.getenv("AIVEN_PASSWORD"))
aiven_engine = create_engine(
    f"mysql+mysqlconnector://{os.getenv('AIVEN_USER')}:{aiven_pw}"
    f"@{os.getenv('AIVEN_HOST')}:{os.getenv('AIVEN_PORT')}/{os.getenv('AIVEN_DB')}",
    connect_args={"ssl_disabled": False},
)

# Turn off the primary-key requirement for every Aiven connection
@event.listens_for(aiven_engine, "connect")
def disable_pk_requirement(dbapi_conn, record):
    cur = dbapi_conn.cursor()
    try:
        cur.execute("SET SESSION sql_require_primary_key = 0")
    except Exception as e:
        print("Could not disable PK requirement:", e)
    finally:
        cur.close()

def clean_name(name):
    name = re.sub(r"\.(xlsx|xls|csv|json|tsv)$", "", name, flags=re.IGNORECASE)
    return re.sub(r"[^0-9a-zA-Z_]", "_", name).lower()

tables = inspect(local_engine).get_table_names()
print("Tables found:", tables)

for table in tables:
    new_name = clean_name(table)
    try:
        df = pd.read_sql(f"SELECT * FROM `{table}`", local_engine)
        df.to_sql(new_name, aiven_engine, if_exists="replace", index=False, chunksize=500)
        print(f"Copied {table} -> {new_name}: {len(df)} rows")
    except Exception as e:
        print(f"FAILED {table}: {str(e)[:200]}")

print("Migration complete!")
