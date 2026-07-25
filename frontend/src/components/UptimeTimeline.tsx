import { UptimeBar } from "./UptimeBar"

type UptimeTimelineProps = {
  data: { timestamp: number; response: number }[]
}

export default function UptimeTimeline({ data }: UptimeTimelineProps) {
  return (
    <div className="flex gap-0.5">
      {data.map((entry, index) => (
        <UptimeBar key={index} response={entry.response} />
      ))}
    </div>
  )
}
