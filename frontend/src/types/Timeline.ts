// Not the literal API shape: get_service_statuses returns status_code in
// seconds, so the fetch mapper must rename the key and scale the timestamp.
export type TimelineEntry = { timestamp: number; statusCode: number }
