
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER benjamin PASSWORD 'SiTRgxsYMxtBbszyie3p1Cwwq';
    ALTER USER benjamin CREATEDB;
    CREATE DATABASE picasa;
    GRANT ALL PRIVILEGES ON DATABASE picasa TO benjamin;
EOSQL
