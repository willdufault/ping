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
      <div className="flex w-full gap-0.5">
        {data.map((entry, index) => (
          <UptimeBar key={index} response={entry.response} />
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-600">
        <span>24h</span>
        <span>{uptime.toFixed(1)}%</span>
      </div>
    </div>
  )
}
