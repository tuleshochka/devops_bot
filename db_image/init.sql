DROP DATABASE IF EXISTS ${DB_DATABASE};
CREATE DATABASE ${DB_DATABASE};

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_REPL_USER}') THEN
     CREATE USER ${DB_REPL_USER} REPLICATION LOGIN PASSWORD '${DB_REPL_PASSWORD}';
   END IF;
END $$;
\c ${DB_DATABASE}
DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS phone_numbers;
CREATE TABLE  phone_numbers (id SERIAL PRIMARY KEY, phone VARCHAR(255));
CREATE TABLE  emails (id SERIAL PRIMARY KEY, email VARCHAR(255));

INSERT INTO emails (email) VALUES ('test@test.ru') ON conflict (email) DO nothing;
INSERT INTO emails (email) VALUES ('test_2@test.ru') ON conflict (email) DO nothing;
INSERT INTO phone_numbers (phone) VALUES ('dsd@ds.d') ON conflict (phone) DO nothing;
INSERT INTO phone_numbers (phone) VALUES ('dsd_test@ds.d') ON conflict (phone) DO nothing;
