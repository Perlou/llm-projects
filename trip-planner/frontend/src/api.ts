import axios from 'axios'
import type { TripPlanResponse, TripRequest } from './types'

const http = axios.create({
  baseURL: '/api',
  timeout: 180_000, // 大模型 + 多轮 MCP 调用，给足超时
})

export async function generatePlan(req: TripRequest): Promise<TripPlanResponse> {
  const { data } = await http.post<TripPlanResponse>('/trip/plan', req)
  return data
}
