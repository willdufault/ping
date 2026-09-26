// One bar in a service's uptime timeline, plus its hover tooltip.
import { StatusTooltip } from "./StatusTooltip"
import { statusColors } from "../constants/responses"
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
      <StatusTooltip
        statusCode={statusCode}
        timestamp={timestamp}
        showBubble
      />
    </div>
  )
}
