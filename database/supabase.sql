-- Supabase-specific configurations and mocks
-- Matches roles and schemas expected by the schema files

-- 1. Create mock roles if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role;
    END IF;
END
$$;

-- 2. Create auth schema and dummy uid() function
CREATE SCHEMA IF NOT EXISTS auth;
CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid AS $$
BEGIN
    -- Return NULL by default, can be overridden if needed
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
