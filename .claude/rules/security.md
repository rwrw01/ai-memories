---
paths:
  - backend/**/*
---
# Security Rules

- All secrets in .env, never hardcode credentials
- Validate and sanitize all user input
- Use HTTPS only (Tailscale Funnel)
- No cloud APIs for AI models — everything runs local
- Pin dependency versions in requirements.txt and package.json
- Address all npm/pip vulnerabilities before merging
- Use parameterized queries for any database access
- Rate limit all API endpoints
