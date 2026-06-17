import type { ResumeData } from '../types/resume'
import { loadAiSettings } from '../utils/aiSettings'

export async function recognizeResumeImage(file: File) {
  const image = await fileToDataUrl(file)
  const response = await fetch('/api/ai/recognize-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image, mimeType: file.type, aiSettings: loadAiSettings() })
  })

  if (!response.ok) {
    throw new Error(await response.text())
  }

  return await response.json() as { resume: Partial<ResumeData> }
}

function fileToDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error('图片读取失败'))
    reader.readAsDataURL(file)
  })
}
