// Status tooltips and the refreshed label; both take a millisecond epoch.
export function formatDateTime(timestamp: number): string {
  return new Date(timestamp)
    .toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    })
    .replace("AM", "am")
    .replace("PM", "pm")
}

export function formatTimeOfDay(timestamp: number): string {
  return new Date(timestamp)
    .toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    })
    .replace("AM", "am")
    .replace("PM", "pm")
}
