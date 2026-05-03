/* 旅行计划相关类型，对齐后端 schemas.py */

export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  address?: string
  location?: Location
  visit_duration?: number
  description?: string
  category?: string
  ticket_price?: number
}

export interface Meal {
  type: string
  name: string
  description?: string
  estimated_cost?: number
}

export interface Hotel {
  name: string
  address?: string
  location?: Location
  price_range?: string
  estimated_cost?: number
}

export interface WeatherInfo {
  date: string
  day_weather?: string
  night_weather?: string
  day_temp?: number
  night_temp?: number
  wind?: string
}

export interface DayPlan {
  date: string
  day_index: number
  description: string
  transportation?: string
  hotel?: Hotel
  attractions: Attraction[]
  meals: Meal[]
}

export interface Budget {
  total_attractions?: number
  total_hotels?: number
  total_meals?: number
  total_transportation?: number
  total?: number
}

export interface TripPlan {
  city: string
  start_date: string
  end_date: string
  days: DayPlan[]
  weather_info: WeatherInfo[]
  overall_suggestions: string
  budget?: Budget
}

export interface TripPlanResponse {
  success: boolean
  message: string
  data: TripPlan | null
}

export interface TripRequest {
  city: string
  start_date: string
  end_date: string
  travel_days: number
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}
