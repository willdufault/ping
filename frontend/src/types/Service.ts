import type { services } from "../constants/services"

export type Service = (typeof services)[number]
