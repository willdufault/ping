type UptimeBarProps = {
  response: number
}

export function UptimeBar({ response }: UptimeBarProps) {
  let color = "bg-gray-400"
  if (response === 200) color = "bg-green-500"
  else if (response === 400) color = "bg-red-500"

  return <div className={`h-16 flex-1 ${color}`} />
}
