-- Read-only role for Metabase.
--
-- RUN THIS ONCE, as the `postgres` superuser on beehive-db.
-- Metabase only ever needs SELECT, and this dashboard is shown to students, so
-- it should not connect with the superuser account.
--
-- 1. Generate a password (do not reuse one):
--        python3 -c "import secrets,string; a=string.ascii_letters+string.digits; print(''.join(secrets.choice(a) for _ in range(32)))"
-- 2. Replace CHANGE_ME below with it.
-- 3. Connect and run:
--        psql "$(railway variables --service beehive-db --kv | grep '^DATABASE_PUBLIC_URL=' | cut -d= -f2-)" -f metabase/00_readonly_role.sql
--    (or paste into the Railway dashboard's query console)
-- 4. Put the same password into Metabase -> Admin -> Databases -> Add -> PostgreSQL.

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'metabase_ro') THEN
    CREATE ROLE metabase_ro LOGIN;
  END IF;
END $$;

ALTER ROLE metabase_ro WITH PASSWORD 'CHANGE_ME';

GRANT CONNECT ON DATABASE railway TO metabase_ro;
GRANT USAGE   ON SCHEMA public    TO metabase_ro;
GRANT SELECT  ON ALL TABLES IN SCHEMA public TO metabase_ro;

-- So tables added by a future migration are readable without re-granting.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metabase_ro;

-- Verify:
--   \du metabase_ro
--   SELECT has_table_privilege('metabase_ro','hive_measurements','SELECT');
