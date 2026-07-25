import { UptimeBar } from "./UptimeBar"

type UptimeTimelineProps = {
  data: { timestamp: number; response: number }[]
}

export default function UptimeTimeline({ data }: UptimeTimelineProps) {
  const uptime =
    Math.trunc(
      (data.filter((e) => e.response === 200).length / data.length) * 1000
    ) / 10

  return (
    <div className="w-full flex flex-col gap-1">
      <div className="flex w-full">
        {data.map((entry, index) => (
          <UptimeBar
            key={index}
            timestamp={entry.timestamp}
            response={entry.response}
            isFirst={index === 0}
            isLast={index === data.length - 1}
          />
        ))}
      </div>
      <div className="flex items-center text-xs text-neutral-400">
        <span>24h</span>
        <hr className="flex-1 border-neutral-500 mx-2 rounded-full" />
        <span>{uptime.toFixed(1)}%</span>
        <hr className="flex-1 border-neutral-500 mx-2 rounded-full" />
        <span>Now</span>
      </div>
    </div>
  )
}
