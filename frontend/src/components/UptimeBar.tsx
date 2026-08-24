import { statusColors, statusLabel } from "../constants/responses"

type UptimeBarProps = {
  timestamp: number
  response: number
  isFirst?: boolean
  isLast?: boolean
}

function formatTime(timestamp: number): string {
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

export function UptimeBar({
  timestamp,
  response,
  isFirst = false,
  isLast = false
}: UptimeBarProps) {
  return (
    <div className="relative flex-1 group">
      <div
        className={`h-16 w-full ${isFirst ? "rounded-l-md" : "border-l"} ${isLast ? "rounded-r-md" : "border-r"} border-neutral-800 hover:opacity-80 ${statusColors[response]}`}
      />
      <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1.5 text-xs whitespace-nowrap">
        <p className="text-neutral-400 mb-0.5">{formatTime(timestamp)}</p>
        <p>
          <span
            className={`inline-block h-2 w-2 rounded-full mt-0.5 mr-1.5 ${statusColors[response]}`}
          />
          {statusLabel(response)}
        </p>
      </div>
    </div>
  )
}
