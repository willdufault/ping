// Not the API shape: the fetch mapper renames status_code and scales the timestamp.
export type TimelineEntry = { timestamp: number; statusCode: number }
