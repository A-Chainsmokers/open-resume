import type { TemplateDef } from '../types/template'

const STORAGE_KEY = 'resume_custom_templates'

export function loadCustomTemplates(): TemplateDef[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) as TemplateDef[] : []
  } catch {
    return []
  }
}

export function saveCustomTemplates(templates: TemplateDef[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates))
}

export function addCustomTemplate(def: TemplateDef): void {
  const list = loadCustomTemplates()
  const idx = list.findIndex((t) => t.id === def.id)
  if (idx >= 0) {
    list[idx] = def
  } else {
    list.push(def)
  }
  saveCustomTemplates(list)
}

export function removeCustomTemplate(id: string): void {
  saveCustomTemplates(loadCustomTemplates().filter((t) => t.id !== id))
}

export function validateTemplateDef(obj: unknown): obj is TemplateDef {
  if (!obj || typeof obj !== 'object') return false
  const d = obj as Record<string, unknown>
  return (
    typeof d.id === 'string' &&
    typeof d.label === 'string' &&
    typeof d.cssClass === 'string' &&
    typeof d.css === 'string' &&
    typeof d.layout === 'string' &&
    Array.isArray(d.sidebarSections) &&
    typeof d.labels === 'object' &&
    d.labels !== null &&
    typeof d.currentText === 'string' &&
    typeof d.profileOutput === 'string' &&
    typeof d.workOutput === 'string' &&
    typeof d.projectsOutput === 'string' &&
    typeof d.educationOutput === 'string' &&
    typeof d.skillsOutput === 'string' &&
    ['center', 'sidebar', 'compact'].includes(d.layout as string)
  )
}
