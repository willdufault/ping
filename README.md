# ping

A fullstack website status tracker that monitors uptime and latency for major sites.

---

## Features

- **Status Dashboard** — view current up/down status, last checked time, and latency for all tracked sites
- **Fixed Sites** — major sites (e.g., Google, Apple) monitored indefinitely
- **Fast Reads** — precomputed latest status in DynamoDB + `Cache-Control` headers (15–60s)
- **Periodic Checks** — EventBridge schedules Lambda to ping all sites automatically

## Architecture

```
Browser (React + Tailwind)
    │
    └── API Gateway
            │
            └── GET /sites   → Lambda → DynamoDB (precomputed status)

EventBridge (scheduled)
    └── Lambda checker → pings each site → writes to DynamoDB
```

**DynamoDB table:** single table, PK = URL — stores site metadata and latest check result per item

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | React, Tailwind CSS, GitHub Pages |
| API       | AWS API Gateway, AWS Lambda       |
| Scheduler | AWS EventBridge                   |
| Database  | AWS DynamoDB                      |

## File Structure

```
ping/
├── frontend/       # React + Tailwind app
├── backend/        # Lambda function handlers (Python)
├── infra/          # AWS CDK app (Python)
└── docs/           # Project documentation
```

## Optional Enhancements

- User-submitted sites for tracking (POST /sites, 1-week TTL)
- Outage reporting (POST /outages)
- Uptime history graphs (separate Checks table: PK = URL, SK = timestamp)
- SNS alerts on status change
- CloudFront CDN for frontend
- Concurrent pings via Python threading to reduce checker Lambda runtime
- Batch sites across multiple Lambda invocations to stay within execution limits
- Consecutive failure threshold before marking a site as down (avoid false positives)
