# Incident Runbook

## Severity Levels
- SEV-1: Customer impact, major outage
- SEV-2: Significant degradation
- SEV-3: Minor issue with workaround

## Initial Response
1. Acknowledge incident in `#incident-updates`.
2. Assign incident commander.
3. Gather timeline and affected services.
4. Post status updates every 15 minutes.

## Engineering Checklist
- Check service health and error rates.
- Validate recent deploys.
- Review queue backlogs and dependency health.
- Roll back if recent release is suspect.

## Communication Checklist
- Internal update template
- Customer support update template
- Resolution summary and follow-up actions

## Post-Incident
- Write incident review within 48 hours.
- Capture root cause and action items.
- Update docs and alerts.
