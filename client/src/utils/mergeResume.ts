import type { ResumeData } from '../types/resume'
import { createId } from './resumeFactory'

export function mergeRecognizedResume(current: ResumeData, recognized: Partial<ResumeData>): ResumeData {
  const next = JSON.parse(JSON.stringify(current)) as ResumeData

  if (recognized.profile) {
    next.profile = { ...next.profile, ...dropEmpty(recognized.profile) }
  }

  if (recognized.education?.length) {
    next.education = mergeArray(next.education, recognized.education, 'edu')
  }

  if (recognized.workExperience?.length) {
    next.workExperience = mergeArray(next.workExperience, recognized.workExperience, 'work')
  }

  if (recognized.projects?.length) {
    next.projects = mergeArray(next.projects, recognized.projects, 'project')
  }

  if (recognized.skills?.length) {
    next.skills = mergeArray(next.skills, recognized.skills, 'skill')
  }

  next.updatedAt = new Date().toISOString()
  return next
}

function mergeArray<T extends { id?: string }>(current: T[], incoming: T[], prefix: string): T[] {
  const map = new Map<string, T>()
  for (const item of current) {
    if (item.id) map.set(item.id, item)
  }

  return incoming.map((item) => {
    if (item.id && map.has(item.id)) {
      return { ...map.get(item.id)!, ...dropEmpty(item) }
    }
    return { ...item, id: item.id || createId(prefix) }
  })
}

function dropEmpty<T extends object>(value: T) {
  return Object.fromEntries(Object.entries(value).filter(([, item]) => item !== '' && item !== undefined && item !== null)) as Partial<T>
}
