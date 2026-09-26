// Fetch one region's status history and map the wire shape to the domain shape.
import axios from "axios"
import { services } from "../constants/services"
import type { ServiceStatusApiResponse } from "../types/ApiResponse"
import type { TimelineData } from "../types/Timeline"
import type { Region } from "../types/Region"

const API_URL = import.meta.env.VITE_API_URL

export async function fetchServiceStatuses(
  region: Region
): Promise<TimelineData> {
  const response = await axios.get<ServiceStatusApiResponse>(
    `${API_URL}/status`,
    { params: { region } }
  )

  const data: TimelineData = {}
  for (const service of services) {
    const entries = response.data[service]
    if (!entries) continue
    // The API sends epoch seconds, the domain type holds milliseconds.
    data[service] = entries.map((entry) => ({
      timestamp: entry.timestamp * 1000,
      statusCode: entry.status_code
    }))
  }
  return data
}
