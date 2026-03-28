# Frontend Setup Guide

## Required Tools
- Node.js 20+
- pnpm
- Docker Desktop (for shared dependencies)

## Repository Setup
1. Clone `payments-web`.
2. Copy `.env.example` to `.env.local`.
3. Install dependencies with pnpm.
4. Start dev server.

## Local Startup
- App URL: `http://localhost:3000`
- API URL should point to local backend.

## Validation
- Log in through local auth flow.
- Open dashboard page.
- Confirm payments list loads.

## Common Failures
- Node version mismatch
- Missing API base URL
- CORS mismatch when backend not configured

## Quick Fixes
- Use `.nvmrc` version.
- Restart app after env changes.
- Verify backend is reachable before frontend debugging.

## Support
Use `#payments-frontend-help` for setup support.
