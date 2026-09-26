// Hover tooltip: a status label, with an optional bubble and timestamp row.
import { statusColors, statusLabel } from "../constants/responses"
import { formatDateTime } from "../utils/formatTime"

type StatusTooltipProps = {
  statusCode: number
  timestamp?: number
  showBubble?: boolean
}

export function StatusTooltip({ statusCode, timestamp, showBubble = false }: StatusTooltipProps) {
  return (
    <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1 text-xs whitespace-nowrap">
      {timestamp !== undefined && (
        <p className="text-neutral-400 mb-0.5">{formatDateTime(timestamp)}</p>
      )}
      <p>
        {showBubble && (
          <span className={`inline-block h-2 w-2 rounded-full mt-0.5 mr-1.5 ${statusColors[statusCode]}`} />
        )}
        {statusLabel(statusCode)}
      </p>
    </div>
  )
}
