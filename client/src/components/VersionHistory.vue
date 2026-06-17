<script setup lang="ts">
import { computed } from 'vue'
import { Modal } from 'ant-design-vue'
import type { ResumeData } from '../types/resume'
import type { VersionRecord } from '../utils/storage'
import { diffResume, type DiffEntry } from '../utils/diffResume'

const props = defineProps<{ history: VersionRecord[]; currentResume: ResumeData }>()
const emit = defineEmits<{ rollback: [id: string]; delete: [id: string]; clear: []; closed: [] }>()

const versionDiffs = computed(() => {
  return props.history.map((record) => ({
    record,
    changes: diffResume(record.resume, props.currentResume),
  }))
})

function confirmRollback(record: VersionRecord) {
  Modal.confirm({
    title: '确认回退',
    content: `确定要回退到 "${record.label}"（${formatTime(record.timestamp)}）的版本吗？当前未保存的修改将丢失。`,
    onOk: () => emit('rollback', record.id),
  })
}

function confirmDelete(record: VersionRecord) {
  Modal.confirm({
    title: '删除历史记录',
    content: `确定删除 "${record.label}"（${formatTime(record.timestamp)}）这条历史记录吗？`,
    okText: '删除',
    okType: 'danger',
    onOk: () => emit('delete', record.id),
  })
}

function confirmClear() {
  Modal.confirm({
    title: '清空历史记录',
    content: '确定清空全部历史记录吗？此操作不可恢复。',
    okText: '清空',
    okType: 'danger',
    onOk: () => emit('clear'),
  })
}

function formatTime(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function groupBySection(entries: DiffEntry[]): Map<string, DiffEntry[]> {
  const grouped = new Map<string, DiffEntry[]>()
  for (const entry of entries) {
    if (!grouped.has(entry.section)) grouped.set(entry.section, [])
    grouped.get(entry.section)!.push(entry)
  }
  return grouped
}
</script>

<template>
  <a-modal open title="历史版本" :footer="null" width="760px" @cancel="emit('closed')">
    <div class="history-toolbar">
      <div class="current-tip">以下差异均为：历史版本 → 当前编辑内容</div>
      <a-button v-if="history.length" danger size="small" @click="confirmClear">清空全部</a-button>
    </div>

    <div v-if="!history.length" class="empty-hint">暂无版本记录，请先点击左侧“保存版本”创建历史快照</div>

    <div v-else class="history-list">
      <div v-for="(item, index) in versionDiffs" :key="item.record.id" class="history-item">
        <div class="history-header">
          <div class="history-index">#{{ index + 1 }}</div>
          <div class="history-body">
            <div class="history-title-row">
              <span class="history-label">{{ item.record.label }}</span>
              <span class="change-count">{{ item.changes.length }} 项变更</span>
            </div>
            <div class="history-time">{{ formatTime(item.record.timestamp) }}</div>
          </div>
          <div class="history-actions">
            <a-button size="small" @click="confirmRollback(item.record)">回退</a-button>
            <a-button size="small" danger @click="confirmDelete(item.record)">删除</a-button>
          </div>
        </div>

        <div v-if="!item.changes.length" class="diff-empty">该历史版本与当前编辑内容一致</div>

        <div v-else class="diff-content">
          <template v-for="[section, entries] in groupBySection(item.changes)" :key="section">
            <div class="diff-section-title">{{ section }}</div>
            <div v-for="(entry, ei) in entries" :key="ei" class="diff-entry">
              <span class="diff-field">{{ entry.field }}</span>
              <span class="diff-old">{{ entry.oldValue }}</span>
              <span class="diff-arrow">→</span>
              <span class="diff-new">{{ entry.newValue }}</span>
            </div>
          </template>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<style scoped>
.history-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.current-tip {
  flex: 1;
  color: #666;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 13px;
}

.empty-hint {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.history-list {
  max-height: 65vh;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.history-index {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #1677ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.history-body {
  flex: 1;
  min-width: 0;
}

.history-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.history-label {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.change-count {
  color: #1677ff;
  background: #e6f4ff;
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 12px;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.diff-empty {
  color: #999;
  background: #fafafa;
  border-radius: 6px;
  padding: 10px;
  margin-top: 10px;
  text-align: center;
  font-size: 13px;
}

.diff-content {
  margin-top: 10px;
}

.diff-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #1677ff;
  margin: 8px 0 4px;
}

.diff-entry {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 6px 8px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.diff-field {
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.diff-old {
  color: #ff4d4f;
  text-decoration: line-through;
  background: #fff1f0;
  padding: 0 4px;
  border-radius: 2px;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diff-new {
  color: #52c41a;
  background: #f6ffed;
  padding: 0 4px;
  border-radius: 2px;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diff-arrow {
  color: #bbb;
  font-size: 11px;
  flex-shrink: 0;
}
</style>
