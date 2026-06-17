import type { ResumeData } from '../types/resume'

const KEY = 'resume_editor_current_resume'
const HISTORY_KEY = 'resume_editor_version_history'
const MAX_VERSIONS = 20

export interface VersionRecord {
  id: string
  timestamp: string
  label: string
  resume: ResumeData
}

export function saveResume(resume: ResumeData) {
  localStorage.setItem(KEY, JSON.stringify({ resume, savedAt: new Date().toISOString() }))
}

export function loadResume(): ResumeData | null {
  const raw = localStorage.getItem(KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return parsed.resume ?? parsed
  } catch {
    return null
  }
}

export function clearResume() {
  localStorage.removeItem(KEY)
  localStorage.removeItem(HISTORY_KEY)
}

export function loadVersionHistory(): VersionRecord[] {
  const raw = localStorage.getItem(HISTORY_KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw)
  } catch {
    return []
  }
}

export function saveVersionHistory(history: VersionRecord[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_VERSIONS)))
}

export function deleteVersion(versionId: string): VersionRecord[] {
  const history = loadVersionHistory().filter((record) => record.id !== versionId)
  saveVersionHistory(history)
  return history
}

export function clearVersionHistory(): VersionRecord[] {
  localStorage.removeItem(HISTORY_KEY)
  return []
}

export function pushVersion(resume: ResumeData, label: string): VersionRecord[] {
  const history = loadVersionHistory()
  const last = history[0]
  if (last && JSON.stringify(last.resume) === JSON.stringify(resume)) {
    return history
  }
  const record: VersionRecord = {
    id: `v_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    timestamp: new Date().toISOString(),
    label,
    resume: JSON.parse(JSON.stringify(resume)),
  }
  history.unshift(record)
  saveVersionHistory(history)
  return history
}
