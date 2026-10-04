// Ping status dashboard: region toggle, per-service uptime bars, freshness label.
import { useEffect, useState } from "react"
import UptimeTimeline from "./components/UptimeTimeline"
import { StatusTooltip } from "./components/StatusTooltip"
import { services, serviceLabels, serviceIcons } from "./constants/services"
import { regions, regionLabels } from "./constants/regions"
import { statusColors } from "./constants/statuses"
import { formatTimeOfDay } from "./utils/formatTime"
import { fetchServiceStatuses } from "./utils/fetchServiceStatuses"
import type { Region } from "./types/Region"
import type { TimelineData } from "./types/Timeline"

export default function App() {
  const [region, setRegion] = useState<Region>("us-east-1")
  // One fetch per region per visit: a region already in the cache is never refetched.
  const [cache, setCache] = useState<Partial<Record<Region, TimelineData>>>({})

  useEffect(() => {
    if (cache[region] !== undefined) return
    fetchServiceStatuses(region).then((fetched) => {
      setCache((previous) => ({ ...previous, [region]: fetched }))
    })
  }, [region, cache])

  const data = cache[region] ?? {}
  const lastRefreshed = data.ec2?.at(-1)?.timestamp

  return (
    <>
      <header className="max-w-md mx-auto px-4 my-8">
        <h1 className="text-2xl">☁️ ping</h1>
      </header>
      <main className="max-w-md mx-auto px-4">
        <div className="flex items-end">
          {regions.map((option, index) => (
            <button
              key={option}
              className={`px-3 py-1 border border-neutral-500 hover:bg-neutral-700 cursor-pointer ${index === 0 ? "rounded-l-md" : "border-l-0"} ${index === regions.length - 1 ? "rounded-r-md" : ""} ${region === option ? "bg-neutral-700" : ""}`}
              onClick={() => setRegion(option)}
            >
              {regionLabels[option]}
            </button>
          ))}
          {lastRefreshed !== undefined && (
            <span className="ml-auto text-xs text-neutral-400">
              Refreshed {formatTimeOfDay(lastRefreshed)}
            </span>
          )}
        </div>
        <div className="mt-4 flex flex-col gap-6">
          {services.map((service) => {
            const entries = data[service]
            if (!entries?.length) return null
            const lastEntry = entries[entries.length - 1]
            return (
              <div key={service} className="flex gap-6">
                <div className="flex flex-col items-start shrink-0 gap-1">
                  <img
                    src={serviceIcons[service]}
                    alt={service}
                    className="h-16 w-16 rounded-md"
                  />
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-neutral-400">
                      {serviceLabels[service]}
                    </span>
                    <div className="relative group">
                      <div
                        className={`h-2 w-2 rounded-full mt-0.5 ${statusColors[lastEntry.status]}`}
                      />
                      <StatusTooltip
                        status={lastEntry.status}
                        message={lastEntry.message}
                      />
                    </div>
                  </div>
                </div>
                <UptimeTimeline data={entries} />
              </div>
            )
          })}
        </div>
        <p className="text-neutral-400 text-xs mt-4">*Global service</p>
      </main>
    </>
  )
}
