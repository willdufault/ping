// Status tooltips and the refreshed label; both take a millisecond epoch.
function formatTimestamp(
  timestamp: number,
  options: Intl.DateTimeFormatOptions
): string {
  return new Date(timestamp)
    .toLocaleString(undefined, options)
    .replace("AM", "am")
    .replace("PM", "pm")
}

export function formatDateTime(timestamp: number): string {
  return formatTimestamp(timestamp, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true
  })
}

export function formatTimeOfDay(timestamp: number): string {
  return formatTimestamp(timestamp, {
    hour: "numeric",
    minute: "2-digit",
    hour12: true
  })
}
