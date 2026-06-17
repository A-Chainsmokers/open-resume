import { defineStore } from 'pinia'
import type { ResumeData } from '../types/resume'
import { createDefaultResume, defaultSectionOrder } from '../utils/resumeFactory'
import { clearVersionHistory, deleteVersion, loadResume, saveResume, loadVersionHistory, saveVersionHistory, pushVersion } from '../utils/storage'
import type { VersionRecord } from '../utils/storage'

export const useResumeStore = defineStore('resume', {
  state: () => {
    const resume = loadResume() ?? createDefaultResume()
    resume.settings.sectionOrder ??= [...defaultSectionOrder]
    resume.profile.gender ??= ''
    resume.profile.age ??= ''
    resume.profile.workYears ??= ''
    resume.profile.expectedSalary ??= ''
    resume.profile.expectedCity ??= resume.profile.city ?? ''
    resume.profile.avatar ??= ''
    resume.profile.summary = toRichText(resume.profile.summary)
    resume.workExperience.forEach((work) => {
      work.summary = toRichText(work.summary)
    })
    resume.projects.forEach((project) => {
      project.responsibilitiesText ??= toRichText(project.responsibilities?.join('\n') ?? '')
      project.achievementsText ??= toRichText(project.achievements?.join('\n') ?? '')
    })
    const history = loadVersionHistory()
    return { resume, lastSavedAt: '', isExporting: false, history }
  },
  actions: {
    touch() {
      this.resume.updatedAt = new Date().toISOString()
      saveResume(this.resume)
      this.lastSavedAt = this.resume.updatedAt
    },
    setResume(resume: ResumeData, label?: string) {
      resume.profile.summary = toRichText(resume.profile.summary)
      resume.workExperience.forEach((work) => {
        work.summary = toRichText(work.summary)
      })
      resume.projects.forEach((project) => {
        project.responsibilitiesText = toRichText(project.responsibilitiesText)
        project.achievementsText = toRichText(project.achievementsText)
      })
      this.history = pushVersion(JSON.parse(JSON.stringify(this.resume)), label || '手动修改')
      this.resume = resume
      this.touch()
    },
    pushHistory(label: string) {
      this.history = pushVersion(JSON.parse(JSON.stringify(this.resume)), label)
    },
    deleteHistory(versionId: string) {
      this.history = deleteVersion(versionId)
    },
    clearHistory() {
      this.history = clearVersionHistory()
    },
    rollbackTo(versionId: string) {
      const target = this.history.find((v) => v.id === versionId)
      if (!target) return
      this.resume = JSON.parse(JSON.stringify(target.resume))
      this.resume.profile.summary = toRichText(this.resume.profile.summary)
      this.resume.workExperience.forEach((work) => { work.summary = toRichText(work.summary) })
      this.resume.projects.forEach((project) => {
        project.responsibilitiesText = toRichText(project.responsibilitiesText)
        project.achievementsText = toRichText(project.achievementsText)
      })
      const idx = this.history.findIndex((v) => v.id === versionId)
      if (idx > 0) this.history = this.history.slice(0, idx)
      saveVersionHistory(this.history)
      this.touch()
    },
    setTemplate(templateId: string) {
      this.history = pushVersion(JSON.parse(JSON.stringify(this.resume)), '切换模板')
      this.resume.templateId = templateId
      this.touch()
    },
    reset() {
      this.history = pushVersion(JSON.parse(JSON.stringify(this.resume)), '重置简历')
      this.resume = createDefaultResume()
      this.touch()
    }
  }
})

function toRichText(value: string) {
  if (!value) return ''
  if (/<[a-z][\s\S]*>/i.test(value)) return value
  return value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => `<p>${line}</p>`)
    .join('')
}
