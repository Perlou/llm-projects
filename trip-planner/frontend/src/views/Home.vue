<script setup lang="ts">
import { computed, ref } from 'vue'
import dayjs, { Dayjs } from 'dayjs'
import { message } from 'ant-design-vue'
import { generatePlan } from '../api'
import type { TripPlan, TripRequest } from '../types'

const props = defineProps<{ loading: boolean }>()
const emit = defineEmits<{
  (e: 'loading', v: boolean): void
  (e: 'ready', plan: TripPlan): void
}>()

const PREFERENCE_OPTIONS = [
  '历史文化', '美食', '自然风光', '购物', '亲子', '小众', '夜生活', '博物馆',
]
const TRANSPORT_OPTIONS = ['公共交通', '自驾', '步行+地铁', '高铁/动车']
const ACCOMMODATION_OPTIONS = ['经济型酒店', '舒适型酒店', '豪华酒店', '青年旅舍', '民宿']

const form = ref({
  city: '北京',
  dateRange: [dayjs(), dayjs().add(2, 'day')] as [Dayjs, Dayjs],
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: ['历史文化', '美食'] as string[],
  free_text_input: '',
})

const travelDays = computed(() => {
  const [s, e] = form.value.dateRange
  return Math.max(1, e.diff(s, 'day') + 1)
})

async function onSubmit() {
  if (!form.value.city) {
    message.warning('请输入目的地城市')
    return
  }
  const [s, e] = form.value.dateRange
  const req: TripRequest = {
    city: form.value.city,
    start_date: s.format('YYYY-MM-DD'),
    end_date: e.format('YYYY-MM-DD'),
    travel_days: travelDays.value,
    transportation: form.value.transportation,
    accommodation: form.value.accommodation,
    preferences: form.value.preferences,
    free_text_input: form.value.free_text_input,
  }
  emit('loading', true)
  try {
    const resp = await generatePlan(req)
    if (resp.success && resp.data) {
      emit('ready', resp.data)
    } else {
      message.error('生成失败：' + (resp.message || '未知错误'))
    }
  } catch (err: any) {
    message.error('请求失败：' + (err?.message ?? err))
  } finally {
    emit('loading', false)
  }
}
</script>

<template>
  <a-card title="规划你的下一次旅行" :bordered="false">
    <a-spin :spinning="props.loading" tip="ReActAgent 正在调用高德 MCP 工具收集素材，请稍候 …">
      <a-form layout="vertical" :model="form">
        <a-form-item label="目的地城市">
          <a-input v-model:value="form.city" placeholder="如：北京 / 上海 / 杭州" />
        </a-form-item>

        <a-form-item :label="`旅行日期（共 ${travelDays} 天）`">
          <a-range-picker v-model:value="form.dateRange" style="width: 100%" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="交通方式">
              <a-select v-model:value="form.transportation" :options="TRANSPORT_OPTIONS.map(v => ({ value: v }))" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="住宿偏好">
              <a-select v-model:value="form.accommodation" :options="ACCOMMODATION_OPTIONS.map(v => ({ value: v }))" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="旅行风格（可多选）">
          <a-select
            v-model:value="form.preferences"
            mode="multiple"
            :options="PREFERENCE_OPTIONS.map(v => ({ value: v }))"
            placeholder="选择风格标签"
          />
        </a-form-item>

        <a-form-item label="额外要求（可选）">
          <a-textarea
            v-model:value="form.free_text_input"
            placeholder="如：希望多安排博物馆 / 避开网红打卡点"
            :rows="3"
          />
        </a-form-item>

        <a-form-item>
          <a-button type="primary" size="large" block :loading="props.loading" @click="onSubmit">
            🚀 生成旅行计划
          </a-button>
        </a-form-item>
      </a-form>
    </a-spin>
  </a-card>
</template>
