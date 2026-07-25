export const regions = ["us-east-1", "us-east-2"] as const

export const regionLabels: Record<(typeof regions)[number], string> = {
  "us-east-1": "ue1",
  "us-east-2": "ue2",
}
