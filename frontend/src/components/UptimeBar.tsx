// One bar in a service's uptime timeline, plus its hover tooltip.
import { statusColors, statusLabel } from "../constants/responses"
import { formatDateTime } from "../utils/formatTime"
import type { TimelineEntry } from "../types/Timeline"

type UptimeBarProps = TimelineEntry & {
  isFirst?: boolean
  isLast?: boolean
}

export function UptimeBar({
  timestamp,
  statusCode,
  isFirst = false,
  isLast = false
}: UptimeBarProps) {
  return (
    <div className="relative flex-1 group">
      <div
        className={`h-16 w-full ${isFirst ? "rounded-l-md" : "border-l"} ${isLast ? "rounded-r-md" : "border-r"} border-neutral-800 hover:opacity-80 ${statusColors[statusCode]}`}
      />
      <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1.5 text-xs whitespace-nowrap">
        <p className="text-neutral-400 mb-0.5">{formatDateTime(timestamp)}</p>
        <p>
          <span
            className={`inline-block h-2 w-2 rounded-full mt-0.5 mr-1.5 ${statusColors[statusCode]}`}
          />
          {statusLabel(statusCode)}
        </p>
      </div>
    </div>
  )
}
