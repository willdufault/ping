import type { Status } from "../enums/status"

export const statusColors: Record<Status, string> = {
  Healthy: "bg-green-400",
  Degraded: "bg-amber-400",
  Outage: "bg-red-500",
  Unknown: "bg-neutral-400",
}