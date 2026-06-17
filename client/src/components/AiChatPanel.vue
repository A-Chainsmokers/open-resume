<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { chatEditResume } from '../api/chatEdit'
import type { ResumeData } from '../types/resume'

function applyChatPatch(current: ResumeData, patch: Partial<ResumeData>): ResumeData {
  const next = JSON.parse(JSON.stringify(current)) as ResumeData

  if (patch.profile) {
    Object.assign(next.profile, Object.fromEntries(
      Object.entries(patch.profile).filter(([, v]) => v !== '' && v != null)
    ))
  }

  if (patch.workExperience?.length) {
    next.workExperience = mergeItems(next.workExperience, patch.workExperience)
  }

  if (patch.education?.length) {
    next.education = mergeItems(next.education, patch.education)
  }

  if (patch.projects?.length) {
    next.projects = mergeItems(next.projects, patch.projects)
  }

  if (patch.skills?.length) {
    next.skills = mergeItems(next.skills, patch.skills)
  }

  next.updatedAt = new Date().toISOString()
  return next
}

function mergeItems<T extends { id?: string }>(current: T[], incoming: T[]): T[] {
  const result = [...current]

  for (const item of incoming) {
    if (item.id) {
      const idx = result.findIndex((e) => e.id === item.id)
      if (idx >= 0) {
        result[idx] = { ...result[idx], ...item }
        continue
      }
    }
    result.push({ ...item })
  }

  return result
}

const props = defineProps<{ resume: ResumeData }>()
const emit = defineEmits<{ applied: [resume: ResumeData]; closed: [] }>()

const input = ref('')
const isSending = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  pendingResume?: ResumeData
}

const messages = ref<ChatMessage[]>([
  { role: 'assistant', content: '告诉我你想如何修改简历，例如：把个人优势改得更适合 Java 后端岗位，或把第一个项目成果写得更量化。' }
])

const showMention = ref(false)
const mentionQuery = ref('')
const mentionCursor = ref(-1)
const selectedIndex = ref(-1)

const mentionItems = computed(() => {
  const items: Array<{ label: string; insert: string }> = []
  props.resume.workExperience.forEach((w, i) => {
    items.push({ label: `工作经历 ${i + 1}: ${w.company} - ${w.position}`, insert: `@工作经历${i + 1}: ${w.company} - ${w.position}` })
  })
  props.resume.projects.forEach((p, i) => {
    items.push({ label: `项目经历 ${i + 1}: ${p.name}`, insert: `@项目经历${i + 1}: ${p.name}` })
  })
  return items
})

const filteredItems = computed(() => {
  if (!mentionQuery.value) return mentionItems.value
  const q = mentionQuery.value.toLowerCase()
  return mentionItems.value.filter(i => i.label.toLowerCase().includes(q))
})

function onInput(e: Event) {
  const el = e.target as HTMLTextAreaElement
  const pos = el.selectionStart
  const val = el.value

  if (pos > 0 && val[pos - 1] === '@') {
    const charBefore = pos > 1 ? val[pos - 2] : ' '
    if (pos === 1 || /[\s(]/.test(charBefore)) {
      showMention.value = true
      mentionQuery.value = ''
      mentionCursor.value = pos - 1
      selectedIndex.value = 0
      return
    }
  }

  if (showMention.value && mentionCursor.value >= 0) {
    const afterAt = val.slice(mentionCursor.value + 1, pos)
    if (afterAt.includes(' ') || pos <= mentionCursor.value) {
      showMention.value = false
      mentionCursor.value = -1
      return
    }
    mentionQuery.value = afterAt
    selectedIndex.value = 0
  }
}

function onKeydown(e: KeyboardEvent) {
  if (showMention.value && filteredItems.value.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value + 1) % filteredItems.value.length
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value - 1 + filteredItems.value.length) % filteredItems.value.length
      return
    }
    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault()
      selectItem(filteredItems.value[selectedIndex.value])
      return
    }
    if (e.key === 'Escape') {
      showMention.value = false
      mentionCursor.value = -1
      return
    }
  }

  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    send()
  }
}

function selectItem(item: { label: string; insert: string }) {
  if (mentionCursor.value < 0) return
  const before = input.value.slice(0, mentionCursor.value)
  const after = input.value.slice(mentionCursor.value + 1 + mentionQuery.value.length)
  input.value = before + item.insert + ' ' + after
  showMention.value = false
  mentionCursor.value = -1
  mentionQuery.value = ''
  nextTick(() => {
    const newPos = before.length + item.insert.length + 1
    textareaRef.value?.setSelectionRange(newPos, newPos)
    textareaRef.value?.focus()
  })
}

function escapeRegex(str: string) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function expandMentions(text: string): string {
  let expanded = text
  props.resume.workExperience.forEach((w, i) => {
    const label = escapeRegex(`${w.company} - ${w.position}`)
    const pattern = new RegExp(`@工作经历${i + 1}: ${label}`, 'g')
    expanded = expanded.replace(pattern, `【工作经历 ${i + 1}】公司：${w.company}，职位：${w.position}，时间：${w.startDate || '?'} - ${w.endDate || (w.isCurrent ? '至今' : '?')}，概述：${w.summary || '无'}`)
  })
  props.resume.projects.forEach((p, i) => {
    const label = escapeRegex(p.name)
    const pattern = new RegExp(`@项目经历${i + 1}: ${label}`, 'g')
    expanded = expanded.replace(pattern, `【项目经历 ${i + 1}】项目名称：${p.name}，角色：${p.role}，描述：${p.description || '无'}，技术栈：${p.techStack.join('、') || '无'}`)
  })
  return expanded
}

async function send() {
  const rawText = input.value.trim()
  if (!rawText) return

  const text = expandMentions(rawText)
  messages.value.push({ role: 'user', content: rawText })
  input.value = ''
  showMention.value = false
  mentionCursor.value = -1
  isSending.value = true

  try {
    const result = await chatEditResume(text, props.resume)
    const pending = applyChatPatch(props.resume, result.resume)
    messages.value.push({ role: 'assistant', content: result.reply || '已生成修改建议，请确认是否应用。', pendingResume: pending })
  } catch (error) {
    messages.value.push({ role: 'assistant', content: error instanceof Error ? error.message : '修改失败' })
  } finally {
    isSending.value = false
  }
}

function applyPending(msg: ChatMessage) {
  if (msg.pendingResume) {
    emit('applied', msg.pendingResume)
    msg.pendingResume = undefined
  }
}

function rejectPending(msg: ChatMessage) {
  msg.pendingResume = undefined
}
</script>

<template>
  <aside class="ai-chat-panel">
    <div class="ai-chat-head">
      <strong>AI 聊天修改</strong>
      <a-button size="small" @click="emit('closed')">关闭</a-button>
    </div>
    <div class="ai-chat-messages">
      <div v-for="(msg, index) in messages" :key="index" class="ai-chat-message" :class="msg.role">
        <div class="message-content">{{ msg.content }}</div>
        <div v-if="msg.role === 'assistant' && msg.pendingResume" class="message-actions">
          <a-button size="small" type="primary" @click="applyPending(msg)">确认修改</a-button>
          <a-button size="small" @click="rejectPending(msg)">拒绝</a-button>
        </div>
      </div>
    </div>
    <div class="ai-chat-input">
      <div class="mention-wrapper">
        <a-textarea
          ref="textareaRef"
          v-model:value="input"
          :rows="4"
          placeholder='输入修改要求，例如：优化工作经历概述，突出 Java、SpringBoot 和项目管理经验。输入 @ 可引用工作经历或项目经历'
          @input="onInput"
          @keydown="onKeydown"
        />
        <div v-if="showMention && filteredItems.length > 0" class="mention-dropdown">
          <div
            v-for="(item, idx) in filteredItems"
            :key="item.insert"
            class="mention-item"
            :class="{ active: idx === selectedIndex }"
            @mousedown.prevent="selectItem(item)"
          >
            {{ item.label }}
          </div>
        </div>
      </div>
      <div class="ai-chat-actions">
        <span class="mention-hint">输入 <code>@</code> 引用工作经历/项目经历</span>
        <a-button type="primary" :loading="isSending" @click="send">{{ isSending ? '修改中...' : '发送并修改' }}</a-button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.mention-wrapper {
  position: relative;
}

.mention-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  z-index: 10;
  margin-bottom: 4px;
}

.mention-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: background 0.15s;
}

.mention-item:hover,
.mention-item.active {
  background: #e6f4ff;
  color: #1677ff;
}

.mention-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.message-content {
  white-space: pre-wrap;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.ai-chat-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.mention-hint {
  font-size: 12px;
  color: #999;
}

.mention-hint code {
  background: #f5f5f5;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  color: #666;
}
</style>
