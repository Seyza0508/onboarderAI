# VPN Setup Guide

## Why VPN Is Required
Internal services, wiki pages, and staging environments are only available over VPN.

## Install Steps
1. Install `Northstar Secure Connect` client.
2. Import company profile from IT portal.
3. Sign in with SSO and complete MFA.
4. Choose region nearest to your office.
5. Verify status shows `Connected`.

## Connectivity Validation
- Open internal wiki homepage.
- Ping internal host: `payments-internal.northstar.local`.
- Open staging dashboard.

## Known Errors
- `CERT_MISSING`: profile not imported.
- `MFA_TIMEOUT`: retry after fresh login.
- `DNS_NOT_RESOLVED`: flush DNS and reconnect.

## Troubleshooting Checklist
- Restart VPN client.
- Disable conflicting local VPN software.
- Update system clock.
- Reboot machine if route table appears stale.

## Escalation
If unresolved after two attempts, contact IT Network Ops with:
- Error code
- Screenshot
- Region selected
- Timestamp
