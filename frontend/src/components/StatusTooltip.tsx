// Hover tooltip: a status label, with an optional bubble and timestamp row.
import { statusColors } from "../constants/statuses"
import { formatDateTime } from "../utils/formatTime"
import type { Status } from "../enums/status"

type StatusTooltipProps = {
  status: Status
  message: string | null
  timestamp?: number
  showBubble?: boolean
}

export function StatusTooltip({ status, message, timestamp, showBubble = false }: StatusTooltipProps) {
  return (
    <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1 text-xs">
      {timestamp !== undefined && (
        <p className="text-neutral-400 mb-0.5 whitespace-nowrap">{formatDateTime(timestamp)}</p>
      )}
      <p className="whitespace-nowrap">
        {showBubble && (
          <span className={`inline-block h-2 w-2 rounded-full mt-0.5 mr-1.5 ${statusColors[status]}`} />
        )}
        {status}
      </p>
      {/* Unknown carries a raw botocore error, so let it wrap instead of nowrap. */}
      {message && <p className="text-neutral-400 max-w-48 break-words">{message}</p>}
    </div>
  )
}