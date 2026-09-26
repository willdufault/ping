// Wire shape from GET /status. Epoch seconds and snake_case, unlike TimelineEntry.
import type { Service } from "./Service"

export type ApiTimelineEntry = { timestamp: number; status_code: number }

export type ServiceStatusApiResponse = Partial<Record<Service, ApiTimelineEntry[]>>
