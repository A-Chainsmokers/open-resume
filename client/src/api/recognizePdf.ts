import type { ResumeData } from '../types/resume'
import { loadAiSettings } from '../utils/aiSettings'
import type { AiSettings } from '../utils/aiSettings'

export async function recognizeResumePdf(file: File, aiSettings?: AiSettings) {
  const settings = aiSettings || loadAiSettings()
  const formData = new FormData()
  formData.append('file', file)
  formData.append('api_key', settings.apiKey || '')
  if (settings.baseUrl) formData.append('base_url', settings.baseUrl)
  if (settings.model) formData.append('model', settings.model)

  const response = await fetch('/api/ai/recognize-pdf', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(await response.text())
  }

  return await response.json() as { resume: Partial<ResumeData> }
}
