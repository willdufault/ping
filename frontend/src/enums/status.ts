// Mirrors backend/lambdas/collect_service_statuses/enums/status.py. Separate
// builds, so the strings are duplicated like regions in constants/regions.ts.
export const Status = {
  Healthy: "Healthy",
  Degraded: "Degraded",
  Outage: "Outage",
  Unknown: "Unknown"
} as const

export type Status = (typeof Status)[keyof typeof Status]

