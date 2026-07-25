type UptimeBarProps = {
  timestamp: number
  response: number
  isFirst?: boolean
  isLast?: boolean
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp)
  const hours24 = date.getHours()
  const minutes = date.getMinutes()
  const period = hours24 >= 12 ? "PM" : "AM"
  const hours12 = hours24 % 12 || 12
  return `${hours12}:${minutes.toString().padStart(2, "0")} ${period}`
}

function statusLabel(response: number): string {
  if (response === 200) return "Operational"
  if (response === 400) return "Degraded"
  return "Server error"
}

function statusColor(response: number): string {
  if (response === 200) return "bg-green-400"
  if (response === 400) return "bg-red-500"
  return "bg-neutral-400"
}

export function UptimeBar({ timestamp, response, isFirst = false, isLast = false }: UptimeBarProps) {
  return (
    <div className="relative flex-1 group">
      <div
        className={`h-16 w-full ${isFirst ? "rounded-l-md" : "border-l"} ${isLast ? "rounded-r-md" : "border-r"} border-neutral-800 hover:opacity-80 ${statusColor(response)}`}
      />
      <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1 text-xs whitespace-nowrap">
        <div className="flex items-center gap-1.5">
          <span>{statusLabel(response)}</span>
          <span className={`h-2 w-2 rounded-full ${statusColor(response)}`} />
        </div>
        <div className="text-neutral-400">{formatTime(timestamp)}</div>
      </div>
    </div>
  )
}
