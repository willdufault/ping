export const statuses = [200, 400, 500] as const

export const statusColors: Record<number, string> = {
  200: "bg-green-400",
  400: "bg-red-500",
  500: "bg-neutral-400",
}

export function statusLabel(response: number): string {
  if (response === 200) return "Operational"
  if (response === 400) return "Degraded"
  return "Server error"
}
