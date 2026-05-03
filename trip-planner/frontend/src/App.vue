<script setup lang="ts">
import { ref } from 'vue'
import type { TripPlan } from './types'
import Home from './views/Home.vue'
import Result from './views/Result.vue'

const plan = ref<TripPlan | null>(null)
const loading = ref(false)

function onPlanReady(p: TripPlan) {
  plan.value = p
}
function onLoading(v: boolean) {
  loading.value = v
}
function onReset() {
  plan.value = null
}
</script>

<template>
  <a-layout class="app">
    <a-layout-header class="header">
      <span class="logo">🌍 ClearAgent 旅行规划助手</span>
      <span class="sub">高德 MCP · ReActAgent · 结构化输出</span>
    </a-layout-header>

    <a-layout-content class="content">
      <Home v-if="!plan" :loading="loading" @loading="onLoading" @ready="onPlanReady" />
      <Result v-else :plan="plan" @reset="onReset" />
    </a-layout-content>

    <a-layout-footer class="footer">
      Powered by <a href="https://pypi.org/project/clear-agent/" target="_blank">clear-agent</a>
      · CC BY-NC-SA 4.0
    </a-layout-footer>
  </a-layout>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  background: #001529;
  color: #fff;
  padding: 0 32px;
}
.logo {
  font-size: 20px;
  font-weight: 600;
}
.sub {
  font-size: 13px;
  color: #9bb3c7;
}
.content {
  max-width: 960px;
  margin: 24px auto;
  padding: 0 16px;
  width: 100%;
}
.footer {
  text-align: center;
  font-size: 13px;
  color: #999;
}
</style>
