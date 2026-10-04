// Wire shape from GET /status. Epoch seconds, unlike TimelineEntry.
import type { Service } from "./Service"
import type { Status } from "../enums/status"

export type ApiTimelineEntry = {
  timestamp: number
  status: Status
  message: string | null
}

export type ServiceStatusApiResponse = Partial<Record<Service, ApiTimelineEntry[]>>