import { loadAiSettings, type AiSettings } from '../utils/aiSettings'

export async function polishText(payload: { field: string; html: string; context?: Record<string, unknown>; aiSettings?: AiSettings }) {
  const response = await fetch('/api/ai/polish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, aiSettings: payload.aiSettings ?? loadAiSettings() })
  })

  if (!response.ok) {
    throw new Error(await response.text())
  }

  return await response.json() as { html: string }
}
