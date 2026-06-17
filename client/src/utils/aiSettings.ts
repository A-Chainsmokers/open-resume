export interface AiSettings {
  baseUrl: string
  apiKey: string
  model: string
}

const KEY = 'resume_editor_ai_settings'

export const defaultAiSettings: AiSettings = {
  baseUrl: 'https://api.openai.com/v1/chat/completions',
  apiKey: '',
  model: 'gpt-4o-mini'
}

export function loadAiSettings(): AiSettings {
  const raw = localStorage.getItem(KEY)
  if (!raw) return { ...defaultAiSettings }

  try {
    return { ...defaultAiSettings, ...JSON.parse(raw) }
  } catch {
    return { ...defaultAiSettings }
  }
}

export function saveAiSettings(settings: AiSettings) {
  localStorage.setItem(KEY, JSON.stringify(settings))
}
