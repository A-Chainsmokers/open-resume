import type { AiSettings } from '../utils/aiSettings'

export async function fetchAiModels(settings: AiSettings) {
  const response = await fetch('/api/ai/models', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  })

  if (!response.ok) {
    throw new Error(await response.text())
  }

  return await response.json() as { models: string[] }
}
