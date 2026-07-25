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
          <UptimeBar key={index} timestamp={entry.timestamp} response={entry.response} />
        ))}
      </div>
      <div className="flex justify-between text-xs text-neutral-400">
        <span>24h</span>
        <span>{uptime.toFixed(1)}%</span>
      </div>
    </div>
  )
}
