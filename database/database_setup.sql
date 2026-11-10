
-- ==========================================================
-- FOREWALK GAMES
-- PostgreSQL Database Setup
-- ==========================================================
-- Creates the required tables and indexes if they
-- do not already exist.
--
-- SAFE TO RE-RUN:
-- Existing tables and records are preserved.
-- ==========================================================

-- 1. MEMBERS
-- Stores registered website members.

CREATE TABLE IF NOT EXISTS public.members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_members_email_lower
ON public.members (LOWER(email));


-- 2. MEMBER SESSIONS
-- Stores login sessions for authenticated members.

CREATE TABLE IF NOT EXISTS public.member_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id BIGINT NOT NULL
        REFERENCES public.members(member_id)
        ON DELETE CASCADE,
    token_hash CHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_member_sessions_member_id
ON public.member_sessions (member_id);


-- 3. LOGIN ATTEMPTS
-- Records login attempts for security monitoring.

CREATE TABLE IF NOT EXISTS public.login_attempts (
    attempt_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    successful BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_login_attempts_email_time
ON public.login_attempts (LOWER(email), attempted_at DESC);


-- ==========================================================
-- 4. APPLICATION USER PERMISSIONS
-- ==========================================================
-- Run this section as a database administrator.
-- The forewalk_app role must already exist.

GRANT USAGE ON SCHEMA public TO forewalk_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE
    public.members,
    public.member_sessions,
    public.login_attempts
TO forewalk_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO forewalk_app;
