<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { useResumeStore } from '../stores/resume'
import AiChatPanel from '../components/AiChatPanel.vue'
import AiSettingsPanel from '../components/AiSettingsPanel.vue'
import VersionHistory from '../components/VersionHistory.vue'
import ResumeEditor from '../components/editor/ResumeEditor.vue'
import ResumePreview from '../components/ResumePreview.vue'
import CustomTemplateManager from '../components/CustomTemplateManager.vue'
import { exportPdf } from '../api/pdf'
import { recognizeResumeImage } from '../api/recognizeImage'
import { recognizeResumePdf } from '../api/recognizePdf'
import { loadAiSettings, type AiSettings } from '../utils/aiSettings'
import { mergeRecognizedResume } from '../utils/mergeResume'
import { getAllTemplateDefs } from '../utils/templates'

const store = useResumeStore()
const templateOptions = ref(getAllTemplateDefs())
const mode = ref<'edit' | 'preview'>('edit')
const showAiSettings = ref(false)
const showAiChat = ref(false)
const showAppSettings = ref(false)
const showHistory = ref(false)
const isSidebarCollapsed = ref(false)
const aiSettings = ref(loadAiSettings())
const isRecognizing = ref(false)
const theme = ref<'light' | 'dark'>('light')
const sectionNames = {
  profile: '基本信息',
  education: '教育经历',
  workExperience: '工作经历',
  projects: '项目经历',
  skills: '技能'
}
const sectionNavItems = computed(() => store.resume.settings.sectionOrder.map((id) => ({ id, name: sectionNames[id] })))
let timer: number | undefined

onMounted(() => {
  const savedTheme = localStorage.getItem('resume_editor_theme')
  if (savedTheme === 'dark' || savedTheme === 'light') theme.value = savedTheme
})

watch(theme, (value) => {
  localStorage.setItem('resume_editor_theme', value)
})

function changed() {
  clearTimeout(timer)
  timer = window.setTimeout(() => store.touch(), 600)
}

function downloadJson() {
  const blob = new Blob([JSON.stringify({ app: 'online-resume-editor', exportedAt: new Date().toISOString(), data: store.resume }, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `resume_${store.resume.profile.name || 'user'}.json`
  link.click()
  URL.revokeObjectURL(url)
}

function triggerFileInput(e: Event) {
  const input = (e.currentTarget as HTMLElement).querySelector<HTMLInputElement>('input[type="file"]')
  if (input && !input.disabled) input.click()
}

function importJson(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    const parsed = JSON.parse(String(reader.result))
    store.setResume(parsed.data ?? parsed.resume ?? parsed, '导入 JSON')
  }
  reader.readAsText(file)
}

async function handleExportPdf() {
  store.isExporting = true
  try {
    await exportPdf(store.resume)
  } catch (error) {
    message.error(error instanceof Error ? error.message : 'PDF 导出失败')
  } finally {
    store.isExporting = false
  }
}

function handleAiSettingsSaved(settings: AiSettings) {
  aiSettings.value = settings
  showAiSettings.value = false
}

function scrollToSection(sectionId: string) {
  mode.value = 'edit'
  requestAnimationFrame(() => {
    document.getElementById(`resume-section-${sectionId}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function handleChatApplied(resume: typeof store.resume) {
  store.setResume(resume, 'AI 聊天修改')
  mode.value = 'edit'
}

async function handleRecognizeImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  if (!file.type.startsWith('image/')) {
    message.warning('请上传图片文件')
    return
  }

  if (file.size > 8 * 1024 * 1024) {
    message.warning('图片不能超过 8MB')
    return
  }

  Modal.confirm({
    title: '确认',
    content: '识别结果会填充并覆盖当前已识别到的对应模块内容，是否继续？',
    onOk: async () => {
      isRecognizing.value = true
      try {
        const result = await recognizeResumeImage(file)
        store.setResume(mergeRecognizedResume(store.resume, result.resume), '图片识别填充')
        mode.value = 'edit'
        message.success('图片识别完成，已填充到简历中')
      } catch (error) {
        message.error(error instanceof Error ? error.message : '图片识别失败')
      } finally {
        isRecognizing.value = false
      }
    }
  })
}

async function handleRecognizePdf(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  if (!file.name.toLowerCase().endsWith('.pdf')) {
    message.warning('请上传 PDF 文件')
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    message.warning('PDF 不能超过 10MB')
    return
  }

  Modal.confirm({
    title: '确认',
    content: '识别结果会填充并覆盖当前已识别到的对应模块内容，是否继续？',
    onOk: async () => {
      isRecognizing.value = true
      try {
        const result = await recognizeResumePdf(file)
        store.setResume(mergeRecognizedResume(store.resume, result.resume), 'PDF 识别填充')
        mode.value = 'edit'
        message.success('PDF 识别完成，已填充到简历中')
      } catch (error) {
        message.error(error instanceof Error ? error.message : 'PDF 识别失败')
      } finally {
        isRecognizing.value = false
      }
    }
  })
}
</script>

<template>
  <main class="app-shell" :data-theme="theme">
    <div class="mobile-tabs"><a-segmented v-model:value="mode" block :options="[{ label: '编辑', value: 'edit' }, { label: '预览', value: 'preview' }]" /></div>
    <AiSettingsPanel v-if="showAiSettings" :settings="aiSettings" @saved="handleAiSettingsSaved" @closed="showAiSettings = false" />

    <a-modal v-model:open="showAppSettings" title="设置" :footer="null" width="680px">
      <div class="app-settings-grid">
        <section class="settings-section">
          <h3>外观</h3>
          <a-form layout="vertical">
            <a-form-item label="简历模板">
              <a-select v-model:value="store.resume.templateId" @change="store.setTemplate(store.resume.templateId)"><a-select-option v-for="tpl in templateOptions" :key="tpl.id" :value="tpl.id">{{ tpl.label }}</a-select-option></a-select>
            </a-form-item>
            <a-form-item label="页面主题">
              <a-segmented v-model:value="theme" :options="[{ label: '浅色', value: 'light' }, { label: '深色', value: 'dark' }]" />
            </a-form-item>
          </a-form>
        </section>
        <CustomTemplateManager @changed="templateOptions = getAllTemplateDefs()" />
        <section class="settings-section">
          <h3>AI 与智能</h3>
          <div class="settings-action-grid">
            <a-button @click="showAiSettings = true">AI 配置</a-button>
            <span class="ant-file-button" :class="{ disabled: isRecognizing }" @click="triggerFileInput"><a-button block :loading="isRecognizing">{{ isRecognizing ? '识别中...' : '识别图片填充' }}</a-button><input type="file" accept="image/*" :disabled="isRecognizing" @change="handleRecognizeImage" /></span>
            <span class="ant-file-button" :class="{ disabled: isRecognizing }" @click="triggerFileInput"><a-button block :loading="isRecognizing">{{ isRecognizing ? '识别中...' : '识别 PDF 填充' }}</a-button><input type="file" accept=".pdf" :disabled="isRecognizing" @change="handleRecognizePdf" /></span>
          </div>
        </section>
        <section class="settings-section">
          <h3>导入导出</h3>
          <div class="settings-action-grid">
            <a-button @click="downloadJson">导出 JSON</a-button>
            <span class="ant-file-button" @click="triggerFileInput"><a-button block>导入 JSON</a-button><input type="file" accept="application/json" @change="importJson" /></span>
            <a-button type="primary" :loading="store.isExporting" @click="handleExportPdf">{{ store.isExporting ? '导出中...' : '导出 PDF' }}</a-button>
          </div>
        </section>
      </div>
    </a-modal>

    <VersionHistory v-if="showHistory" :history="store.history" :current-resume="store.resume" @rollback="store.rollbackTo" @delete="store.deleteHistory" @clear="store.clearHistory" @closed="showHistory = false" />

    <section class="workspace" :class="{ withChat: showAiChat, sidebarCollapsed: isSidebarCollapsed }">
      <aside class="side-nav" :class="{ hiddenMobile: mode !== 'edit', collapsed: isSidebarCollapsed }">
        <div class="side-nav-top">
          <div class="side-nav-brand"><span class="brand-mark">RE</span><strong v-if="!isSidebarCollapsed">简历编辑器</strong></div>
          <div v-if="!isSidebarCollapsed" class="side-nav-title">简历模块</div>
        </div>
        <div class="side-nav-list">
          <button v-for="item in sectionNavItems" :key="item.id" type="button" class="side-nav-item" :title="item.name" @click="scrollToSection(item.id)"><span>{{ item.name.slice(0, 1) }}</span><b v-if="!isSidebarCollapsed">{{ item.name }}</b></button>
        </div>
        <div class="side-nav-bottom">
          <button type="button" class="side-nav-item" @click="isSidebarCollapsed = !isSidebarCollapsed"><span>{{ isSidebarCollapsed ? '展' : '折' }}</span><b v-if="!isSidebarCollapsed">折叠</b></button>
          <button type="button" class="side-nav-item" @click="showAiChat = !showAiChat"><span>AI</span><b v-if="!isSidebarCollapsed">{{ showAiChat ? '关闭AI' : 'AI聊天' }}</b></button>
          <button type="button" class="side-nav-item" @click="showAppSettings = true"><span>设</span><b v-if="!isSidebarCollapsed">设置</b></button>
          <button type="button" class="side-nav-item" @click="showHistory = true"><span>历</span><b v-if="!isSidebarCollapsed">历史版本</b></button>
          <button type="button" class="side-nav-item" @click="store.pushHistory('手动保存')"><span>存</span><b v-if="!isSidebarCollapsed">保存版本</b></button>
        </div>
      </aside>
      <aside class="editor-pane" :class="{ hiddenMobile: mode !== 'edit' }"><ResumeEditor v-model="store.resume" @changed="changed" /></aside>
      <section class="preview-pane" :class="{ hiddenMobile: mode !== 'preview' }"><div class="paper-stage"><ResumePreview :resume="store.resume" /></div></section>
      <AiChatPanel v-if="showAiChat" :resume="store.resume" @applied="handleChatApplied" @closed="showAiChat = false" />
    </section>
  </main>
</template>
