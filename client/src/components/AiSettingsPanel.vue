<script setup lang="ts">
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { fetchAiModels } from '../api/aiModels'
import type { AiSettings } from '../utils/aiSettings'
import { defaultAiSettings, saveAiSettings } from '../utils/aiSettings'

const props = defineProps<{ settings: AiSettings }>()
const emit = defineEmits<{ saved: [settings: AiSettings]; closed: [] }>()
const form = reactive<AiSettings>({ ...props.settings })
const models = ref<string[]>([])
const isLoadingModels = ref(false)

function save() {
  const settings = { ...form }
  saveAiSettings(settings)
  emit('saved', settings)
}

function reset() {
  Object.assign(form, defaultAiSettings)
  models.value = []
}

async function loadModels() {
  isLoadingModels.value = true
  try {
    const result = await fetchAiModels({ ...form })
    models.value = result.models
    if (!form.model && result.models[0]) form.model = result.models[0]
    if (!result.models.length) message.warning('没有获取到模型列表')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '获取模型失败')
  } finally {
    isLoadingModels.value = false
  }
}
</script>

<template>
  <a-modal open title="AI 配置" :footer="null" width="620px" @cancel="emit('closed')">
    <section class="ai-settings-form">
      <label>接口地址<a-input v-model:value="form.baseUrl" placeholder="https://api.openai.com/v1/chat/completions" /></label>
      <label>API Key<a-input-password v-model:value="form.apiKey" placeholder="sk-..." autocomplete="off" /></label>
      <div class="field-block">
        <span>模型</span>
        <div class="model-picker">
          <a-select v-if="models.length" v-model:value="form.model" style="width: 100%"><a-select-option v-for="model in models" :key="model" :value="model">{{ model }}</a-select-option></a-select>
          <a-input v-else v-model:value="form.model" placeholder="gpt-4o-mini" />
          <a-button :loading="isLoadingModels" @click="loadModels">{{ isLoadingModels ? '获取中...' : '获取模型' }}</a-button>
        </div>
      </div>
      <p class="settings-tip">配置仅保存在当前浏览器 localStorage 中。留空 API Key 时，后端会使用本地规则润色或服务器环境变量。</p>
      <div class="settings-actions">
        <a-button @click="reset">恢复默认</a-button>
        <a-button type="primary" @click="save">保存配置</a-button>
      </div>
    </section>
  </a-modal>
</template>
