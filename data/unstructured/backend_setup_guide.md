# Backend Setup Guide

## Required Tools
- Python 3.11+
- Docker Desktop
- Make
- PostgreSQL client tools

## Repository Setup
1. Clone `payments-api`.
2. Copy `.env.example` to `.env.local`.
3. Run dependency install.
4. Start local services with Docker Compose.

## Local Startup
1. Run database migrations.
2. Start API server.
3. Run test suite.
4. Verify health endpoint.

## Expected Local Services
- API: `http://localhost:8000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

## Common Setup Failures
- Dependency install fails due to Python version mismatch.
- Containers fail because Docker engine is not running.
- Database connection fails due to stale credentials.

## First Debug Actions
- Check `.env.local` variables.
- Check Docker container logs.
- Re-run migrations.

## Support
For backend setup blockers, contact `#payments-backend-help`.
