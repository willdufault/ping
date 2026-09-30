# ☁️ ping

Shows whether AWS services are up.

Every 30 minutes a scheduled job makes a small API call to each service in each
region and saves the result. The frontend draws those results as a 24-hour bar
per service.

## Features

- **Real checks** — each one is a live API call to AWS, not a scrape of the AWS
  status page
- **Region switcher** — us-east-1 and us-east-2, fetched once per region per visit
- **24h timeline** — 48 half-hour blocks per service, hover for the time and status
- **Four states** — Healthy, Degraded, Outage, Unknown, with the reason shown
- **Last checked** — shown in the header

## How It Works

```
Every 30 minutes (America/New_York)
    └── check Lambda, runs in us-west-2
        |   calls each service in each region
        |   5 services x 2 regions, 4 at a time
        └── saves results to DynamoDB

Browser (React + Vite, dev server on :5173)
    └── API Gateway
            └── GET /status?region=us-east-1
                    └── read Lambda
                            └── reads one region out of DynamoDB
```

The check job runs in us-west-2 on purpose. If us-east-1 or us-east-2 goes down,
the job that watches it is unaffected.

## Status

Each check stores a status and a message. A check that succeeds in under 3
seconds is healthy; anything else is one of the three problem states.

| Status     | Message               | Meaning                                        |
| ---------- | --------------------- | ---------------------------------------------- |
| `Healthy`  | none                  | the call worked, in under 3 seconds            |
| `Degraded` | `Increased latency`   | the call worked, but took 3 seconds or more    |
| `Degraded` | `Throttling`          | the service replied 429 or a throttle code    |
| `Outage`   | `Service error`       | the service replied with a 5xx                 |
| `Outage`   | `Service unreachable` | no reply at all within 5 seconds               |
| `Unknown`  | the raw error         | we got an error, but it is not a service fault |

Two thresholds, and they are not the same number. `LATENCY_THRESHOLD_SECONDS` (3)
decides whether a working call is healthy or degraded. `TIMEOUT_SECONDS` (5) is
botocore's socket timeout, and anything past it raises a read timeout, which is
an outage. Between the two sits the degraded window.

Throttle codes are matched by name rather than by status, because AWS does not
send them consistently: `Throttling` arrives as 400, `SlowDown` and
`RequestLimitExceeded` as 503, and `RequestThrottled` as 403. Only 429 is
reliable enough to check on its own.

`Unknown` is the fallback for anything that is our fault rather than the
service's — expired credentials, a bad region, a parameter botocore rejected.
Those used to be reported as the service being down.

## Data

One DynamoDB table, `ping_status_history`. One item per region and service:

- `PK` = `REGION#<region>`
- `SK` = `SERVICE#<service>`
- `status_history` = list of `{timestamp, status, message}`, trimmed to the last
  48 entries, which is 24 hours at this schedule

Each check reads the item, appends to the list, and writes it back. Two runs at
the same time can lose a datapoint.

## API

`GET /status?region=<region>`

`region` is optional and defaults to the first region in the list. An unknown
region returns `400` so a typo is not mistaken for "no data". Anything
unexpected returns `500`.

The region list is written once in `infra/app.py` and handed to both Lambdas
through an environment variable. The frontend has its own copy in
`src/constants/regions.ts`, so both sides need updating.

## Stack

| Part      | What                                       |
| --------- | ------------------------------------------ |
| Frontend  | React 19, TypeScript, Vite, Tailwind CSS 4 |
| API       | API Gateway, Lambda (Python 3.13)          |
| Schedule  | EventBridge Scheduler                      |
| Database  | DynamoDB                                   |
| Setup     | AWS CDK v2 (Python)                        |

## Layout

```
ping/
├── frontend/   # React app (components, constants, types, utils)
├── backend/
│   └── lambdas/
│       ├── collect_service_statuses/  # the scheduled checker
│       └── get_service_statuses/      # reads one region's history
├── infra/
│   ├── app.py            # CDK entry point, region list
│   └── stacks/           # root, database, api, refresh
└── TODO.md
```

## Tooling

Needs Node.js, the AWS CDK CLI (global npm install), [uv](https://docs.astral.sh/uv/),
and AWS credentials. `cdk.json` does not pin a profile, so the CLI falls back to
your default profile, or to the `AWS_*` environment variables if those are set.

### Frontend

```sh
cd frontend
npm install
npm run dev      # dev server on :5173
npm run build    # type check, then build
npm run lint
npm run preview  # serve the built files
```

Create `frontend/.env` with `VITE_API_URL` set to the API Gateway URL. It is
gitignored, so it is not in the repo.

The API only allows requests from `http://localhost:5173` right now, so the
dashboard runs from the dev server until that is widened.

### Backend

Nothing to run locally. Both handlers only run as Lambdas. CDK bundles their
dependencies at deploy time, so edits in `backend/lambdas/` show up after a
deploy.

To type check:

```sh
cd backend
uv run --with pyright pyright lambdas
```

There is no pyright config, so it uses the defaults. It currently reports 12
errors, all on `get_service_statuses/index.py:41`, where the `boto3-stubs` type
for an item attribute is a union of every possible value. Treat that as the
baseline rather than a clean run.

### Infrastructure

```sh
cd infra
uv sync
cdk synth     # print the generated CloudFormation
cdk diff      # what would change
cdk deploy
```

`cdk` is installed globally, not as a project dependency. `cdk.json` runs the
app itself with `uv run app.py`, which is what `uv sync` above is for.

`REGIONS` in `infra/app.py` drives the checker, the API, and the frontend. Adding
a region there also means adding it to `frontend/src/constants/regions.ts`.
