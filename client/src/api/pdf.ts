import type { ResumeData } from '../types/resume'

export async function exportPdf(resume: ResumeData) {
  const response = await fetch('/api/pdf/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume, templateId: resume.templateId })
  })
  if (!response.ok) throw new Error(await response.text())
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${resume.profile.name || 'resume'}_${resume.profile.headline || '简历'}.pdf`
  link.click()
  URL.revokeObjectURL(url)
}
