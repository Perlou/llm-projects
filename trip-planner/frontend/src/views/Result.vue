<script setup lang="ts">
import { computed } from 'vue'
import type { TripPlan } from '../types'

const props = defineProps<{ plan: TripPlan }>()
const emit = defineEmits<{ (e: 'reset'): void }>()

const weatherByDate = computed(() => {
  const map: Record<string, any> = {}
  for (const w of props.plan.weather_info ?? []) {
    map[w.date] = w
  }
  return map
})

const mealLabel: Record<string, string> = {
  breakfast: '🥣 早餐',
  lunch: '🍜 午餐',
  dinner: '🍱 晚餐',
}
</script>

<template>
  <div class="result">
    <a-page-header :title="`${plan.city} · ${plan.start_date} ~ ${plan.end_date}`" :sub-title="`共 ${plan.days.length} 天`" @back="emit('reset')" />

    <a-alert
      v-if="plan.overall_suggestions"
      :message="plan.overall_suggestions"
      type="info"
      show-icon
      style="margin-bottom: 16px"
    />

    <a-card v-if="plan.budget" title="💰 预算估算" size="small" style="margin-bottom: 16px">
      <a-descriptions :column="{ xs: 1, sm: 2, md: 4 }" size="small">
        <a-descriptions-item label="景点">¥ {{ plan.budget.total_attractions ?? 0 }}</a-descriptions-item>
        <a-descriptions-item label="酒店">¥ {{ plan.budget.total_hotels ?? 0 }}</a-descriptions-item>
        <a-descriptions-item label="餐饮">¥ {{ plan.budget.total_meals ?? 0 }}</a-descriptions-item>
        <a-descriptions-item label="交通">¥ {{ plan.budget.total_transportation ?? 0 }}</a-descriptions-item>
      </a-descriptions>
      <a-divider style="margin: 12px 0" />
      <strong>合计：¥ {{ plan.budget.total ?? 0 }}</strong>
    </a-card>

    <a-collapse :default-active-key="plan.days.map(d => d.date)" accordion>
      <a-collapse-panel
        v-for="day in plan.days"
        :key="day.date"
        :header="`Day ${day.day_index + 1} · ${day.date} — ${day.description}`"
      >
        <a-descriptions :column="{ xs: 1, sm: 2 }" size="small" style="margin-bottom: 8px">
          <a-descriptions-item label="交通">{{ day.transportation }}</a-descriptions-item>
          <a-descriptions-item v-if="weatherByDate[day.date]" label="天气">
            {{ weatherByDate[day.date].day_weather }} / {{ weatherByDate[day.date].night_weather }}
            ·
            {{ weatherByDate[day.date].day_temp }}℃ / {{ weatherByDate[day.date].night_temp }}℃
            <span v-if="weatherByDate[day.date].wind"> · {{ weatherByDate[day.date].wind }}</span>
          </a-descriptions-item>
        </a-descriptions>

        <a-card v-if="day.hotel" type="inner" title="🏨 推荐酒店" size="small" style="margin-bottom: 12px">
          <strong>{{ day.hotel.name }}</strong>
          <div class="muted">{{ day.hotel.address }}</div>
          <div v-if="day.hotel.price_range || day.hotel.estimated_cost" class="muted">
            价格：{{ day.hotel.price_range }}
            <span v-if="day.hotel.estimated_cost"> · 约 ¥{{ day.hotel.estimated_cost }}/晚</span>
          </div>
        </a-card>

        <a-card type="inner" title="📍 当日景点" size="small" style="margin-bottom: 12px">
          <a-list :data-source="day.attractions" item-layout="horizontal">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <span>{{ item.name }}</span>
                    <a-tag v-if="item.category" color="blue" style="margin-left: 8px">{{ item.category }}</a-tag>
                    <a-tag v-if="item.ticket_price" color="orange">¥{{ item.ticket_price }}</a-tag>
                  </template>
                  <template #description>
                    <div>{{ item.description }}</div>
                    <div class="muted">
                      📍 {{ item.address }}
                      <span v-if="item.visit_duration"> · 建议游览 {{ item.visit_duration }} 分钟</span>
                    </div>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>

        <a-card type="inner" title="🍽️ 餐饮推荐" size="small">
          <a-row :gutter="16">
            <a-col v-for="meal in day.meals" :key="meal.type" :span="8">
              <div class="meal">
                <div class="meal-type">{{ mealLabel[meal.type] ?? meal.type }}</div>
                <div class="meal-name">{{ meal.name }}</div>
                <div v-if="meal.description" class="muted">{{ meal.description }}</div>
                <div v-if="meal.estimated_cost" class="muted">约 ¥{{ meal.estimated_cost }}</div>
              </div>
            </a-col>
          </a-row>
        </a-card>
      </a-collapse-panel>
    </a-collapse>

    <a-button block style="margin-top: 16px" @click="emit('reset')">↩ 重新规划</a-button>
  </div>
</template>

<style scoped>
.muted {
  color: #888;
  font-size: 13px;
}
.meal {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 12px;
  height: 100%;
}
.meal-type {
  font-weight: 600;
  margin-bottom: 4px;
}
.meal-name {
  font-size: 14px;
  margin-bottom: 4px;
}
</style>
