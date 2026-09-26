# TODO

## Feat

- add Last refreshed xyz to ui

## Bugs

- **Timestamp units are mismatched.** `collect_service_statuses/index.py` stores
  `int(time.time())` in seconds, but the frontend mock in `App.tsx` builds
  `Date.now()` values in milliseconds and `UptimeBar` renders with
  `new Date(timestamp)`. Wiring up the real fetch without converting will render
  every bar as Jan 1970. Convert at the fetch boundary and decide which unit the
  `TimelineEntry.timestamp` field is meant to hold.

## Wiring up the frontend

`App.tsx` still renders `generateData()` mock data. Replacing it needs a decision
on what to render before the first response arrives, plus loading and error
states, and a refetch when the region toggle changes.

The fetch mapper has two jobs, both stemming from the API boundary: rename
`status_code` to `statusCode` to match the camelCase prop convention, and
convert the writer's epoch seconds to the milliseconds `UptimeBar` passes to
`new Date`.

## Storage model

- **One item per data point instead of a capped array.** Current items are
  `PK=REGION#<region>`, `SK=SERVICE#<service>` with a `status_history` array
  written read-modify-write. Using `SK=SERVICE#<service>#<epoch>` makes
  `put_item` idempotent, which removes the lost-update risk called out in
  `collect_service_statuses` (the 30-minute schedule makes overlapping
  invocations unlikely but does not prevent them, so an EventBridge retry or a
  manual concurrent invoke can drop a point). It also turns a missed write into a
  visible gap in the key sequence instead of the silent hole in the array.
  Costs: needs a DynamoDB TTL on an `expires_at` attribute for cleanup, and a
  full region view reads 240 items instead of 5, roughly 3 RCU to roughly 30.
- **The region list is duplicated between infra and the frontend.** Both Lambdas
  now read the `regions` environment variable, which CDK sets from the single
  `REGIONS` list in `infra/app.py`, so the backend cannot drift internally.
  `frontend/src/constants/regions.ts` is still a separate copy, and a region
  added on one side but not the other means the UI offers a region the API
  rejects with 400, or hides a region that is being collected. Serving the list
  from the API, or generating the frontend constant, would close this.

## Fragility

- **The `REGION#` / `SERVICE#` key prefixes are duplicated across two Lambdas
  and cannot be shared,** because `Code.from_asset` packages each Lambda
  directory separately. Editing one side silently breaks the other. A contract
  test that writes then reads through the real table would catch this.
- **CORS is hardcoded to `http://localhost:5173`** in `api_stack.py`, so
  anything other than local dev is blocked.
