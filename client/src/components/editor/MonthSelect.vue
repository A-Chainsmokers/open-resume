<script setup lang="ts">
const model = defineModel<string>({ required: true })

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 45 }, (_, index) => currentYear + 3 - index)
const months = Array.from({ length: 12 }, (_, index) => String(index + 1).padStart(2, '0'))

function update(part: 'year' | 'month', value: string) {
  const [year = '', month = ''] = (model.value || '').split('-')
  model.value = part === 'year' ? `${value}-${month || '01'}` : `${year || currentYear}-${value}`
}
</script>

<template>
  <div class="month-select">
    <a-select :value="(model || '').split('-')[0]" placeholder="年份" @change="(value: string) => update('year', value)">
      <a-select-option v-for="year in years" :key="year" :value="String(year)">{{ year }}</a-select-option>
    </a-select>
    <a-select :value="(model || '').split('-')[1]" placeholder="月份" @change="(value: string) => update('month', value)">
      <a-select-option v-for="month in months" :key="month" :value="month">{{ month }}</a-select-option>
    </a-select>
  </div>
</template>
