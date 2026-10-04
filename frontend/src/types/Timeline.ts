// Not the API shape: the fetch mapper only scales the timestamp.
import type { Service } from "./Service"
import type { Status } from "../enums/status"

export type TimelineEntry = {
  timestamp: number
  status: Status
  message: string | null
}

// A service with no collected history yet is absent, not empty.
export type TimelineData = Partial<Record<Service, TimelineEntry[]>>