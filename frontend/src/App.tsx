import { useState } from "react"
import axios from "axios"
import UptimeTimeline from "./components/UptimeTimeline"
import { services, serviceLabels, serviceIcons } from "./constants/services"
import { regions, regionLabels } from "./constants/regions"
import { statuses, statusColors, statusLabel } from "./constants/responses"
import type { Service } from "./types/Service"
import type { Region } from "./types/Region"
import type { TimelineEntry } from "./types/Timeline"

function generateData(): Record<Region, Record<Service, TimelineEntry[]>> {
  const result = {} as Record<Region, Record<Service, TimelineEntry[]>>
  for (const region of regions) {
    result[region] = {} as Record<Service, TimelineEntry[]>
    for (const service of services) {
      result[region][service] = Array.from({ length: 48 }, (_, i) => ({
        timestamp: Date.now() - (47 - i) * 30 * 60 * 1000,
        response: statuses[Math.floor(Math.random() * statuses.length)]
      }))
    }
  }
  return result
}

const mockData = generateData()

export default function App() {
  const [region, setRegion] = useState<Region>("us-east-1")
  const API_URL = import.meta.env.VITE_API_URL

  async function handleGetHello(): Promise<void> {
    const response = await axios.get(`${API_URL}/hello`)
    console.log(response.data)
  }

  async function handleGetEndpoints(): Promise<void> {
    const response = await axios.get(`${API_URL}/endpoints`)
    console.log(response.data)
  }

  return (
    <>
      <header className="text-center border-b border-neutral-500 bg-neutral-800 px-4 py-3 mb-4">
        <h1 className="text-2xl">🛰️ ping</h1>
      </header>
      <main className="max-w-md mx-auto px-4">
        <div className="flex mt-4">
          <button
            className={`px-3 py-1 rounded-l-md border border-neutral-500 hover:bg-neutral-700 cursor-pointer ${region === "us-east-1" ? "bg-neutral-700" : ""}`}
            onClick={() => setRegion("us-east-1")}
          >
            {regionLabels["us-east-1"]}
          </button>
          <button
            className={`px-3 py-1 rounded-r-md border border-l-0 border-neutral-500 hover:bg-neutral-700 cursor-pointer ${region === "us-east-2" ? "bg-neutral-700" : ""}`}
            onClick={() => setRegion("us-east-2")}
          >
            {regionLabels["us-east-2"]}
          </button>
        </div>
        <div className="mt-4 flex flex-col gap-6">
          {services.map((service) => {
            const data = mockData[region][service]
            const lastResponse = data[data.length - 1].response
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
                        className={`h-2 w-2 rounded-full mt-0.5 ${statusColors[lastResponse]}`}
                      />
                      <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 hidden group-hover:block z-10 bg-neutral-800 border border-neutral-500 rounded shadow-lg px-2 py-1 text-xs whitespace-nowrap">
                        <p>{statusLabel(lastResponse)}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <UptimeTimeline data={data} />
              </div>
            )
          })}
        </div>
        <p className="text-neutral-400 text-xs mt-4">*ue1 only</p>
      </main>
    </>
  )
}
