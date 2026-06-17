import type { ResumeData } from '../types/resume'
import { loadAiSettings } from '../utils/aiSettings'

export async function chatEditResume(message: string, resume: ResumeData) {
  const response = await fetch('/api/ai/chat-edit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, resume, aiSettings: loadAiSettings() })
  })

  if (!response.ok) {
    throw new Error(await response.text())
  }

  return await response.json() as { reply: string; resume: Partial<ResumeData> }
}
