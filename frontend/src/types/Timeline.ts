// Not the API shape: the fetch mapper renames status_code and scales the timestamp.
import type { Service } from "./Service"

export type TimelineEntry = { timestamp: number; statusCode: number }

// A service with no collected history yet is absent, not empty.
export type TimelineData = Partial<Record<Service, TimelineEntry[]>>
