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
- **Unknown `region` returns `200 {}`.** `get_service_statuses/index.py` accepts
  any `?region=` value, so a typo looks identical to "no data yet". Validate
  against the known set and return 400.

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
- **`DEFAULT_REGION` duplicates `REGIONS`.** `get_service_statuses/index.py`
  hardcodes `us-east-1` separately from the writer's `REGIONS` list, so the
  default drifts silently. Either validate both against a shared constant or have
  CDK inject the region list into both Lambdas as an environment variable.

## Fragility

- **The `REGION#` / `SERVICE#` key prefixes are duplicated across two Lambdas
  and cannot be shared,** because `Code.from_asset` packages each Lambda
  directory separately. Editing one side silently breaks the other. A contract
  test that writes then reads through the real table would catch this.
- **CORS is hardcoded to `http://localhost:5173`** in `api_stack.py`, so
  anything other than local dev is blocked.
- **`app.py` has an f-string with no placeholders** (ruff `F541`).
