import { useState } from "react"
import axios from "axios"
import UptimeTimeline from "./components/UptimeTimeline"

const statuses = [200, 400, 500]
const services = ["EC2", "Lambda", "S3", "DDB"]
const regions = ["ue1", "ue2"] as const

type Region = (typeof regions)[number]
type Service = (typeof services)[number]
type TimelineEntry = { timestamp: number; response: number }

function generateData(): Record<Region, Record<Service, TimelineEntry[]>> {
  const result = {} as Record<Region, Record<Service, TimelineEntry[]>>
  for (const region of regions) {
    result[region] = {} as Record<Service, TimelineEntry[]>
    for (const service of services) {
      result[region][service] = Array.from({ length: 48 }, (_, i) => ({
        timestamp: i,
        response: statuses[Math.floor(Math.random() * statuses.length)],
      }))
    }
  }
  return result
}

const mockData = generateData()

export default function App() {
  const [region, setRegion] = useState<Region>("ue1")
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
      <header className="text-center border-b border-gray-200 bg-gray-100 px-4 py-3 mb-4">
        <h1 className="text-2xl">🛰️ ping</h1>
      </header>
      <main className="max-w-md mx-auto px-4">
        <div className="flex gap-2">
          <button
            className="border border-gray-300 rounded px-3 py-1"
            onClick={handleGetHello}
          >
            get hello
          </button>
          <button
            className="border border-gray-300 rounded px-3 py-1"
            onClick={handleGetEndpoints}
          >
            get endpoints
          </button>
        </div>
        <div className="flex mt-4">
          <button
            className={`px-3 py-1 rounded-l border border-gray-300 cursor-pointer ${region === "ue1" ? "bg-gray-200" : ""}`}
            onClick={() => setRegion("ue1")}
          >
            ue1
          </button>
          <button
            className={`px-3 py-1 rounded-r border border-l-0 border-gray-300 cursor-pointer ${region === "ue2" ? "bg-gray-200" : ""}`}
            onClick={() => setRegion("ue2")}
          >
            ue2
          </button>
        </div>
        <div className="mt-4 flex flex-col gap-2">
          {services.map((service) => (
            <div key={service}>
              <p className="text-sm text-gray-600">{service}</p>
              <UptimeTimeline data={mockData[region][service]} />
            </div>
          ))}
        </div>
      </main>
    </>
  )
}
