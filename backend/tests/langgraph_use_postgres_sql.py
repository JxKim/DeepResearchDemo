from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
pg_connection_url = "postgresql+psycopg://smartagent_user:smartagent_pass@localhost:5432/smartagent_db"
connection = AsyncConnection(pgconn=pg_connection_url)
# AsyncPostgresSaver(conn=pg_connection_url)
