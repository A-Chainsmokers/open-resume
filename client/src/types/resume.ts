export type SkillLevel = '了解' | '熟悉' | '熟练' | '精通' | ''
export type ResumeSectionId = 'profile' | 'workExperience' | 'projects' | 'education' | 'skills'

export interface ResumeData {
  schemaVersion: string
  id: string
  title: string
  templateId: string
  language: string
  createdAt: string
  updatedAt: string
  profile: Profile
  education: Education[]
  workExperience: WorkExperience[]
  projects: Project[]
  skills: SkillGroup[]
  certificates: Certificate[]
  customSections: CustomSection[]
  settings: ResumeSettings
}

export interface Profile {
  name: string
  headline: string
  phone: string
  email: string
  city: string
  gender: string
  age: string
  workYears: string
  expectedSalary: string
  expectedCity: string
  avatar: string
  website: string
  github: string
  summary: string
}

export interface Education {
  id: string
  school: string
  degree: string
  major: string
  startDate: string
  endDate: string
  description: string[]
}

export interface WorkExperience {
  id: string
  company: string
  position: string
  city: string
  startDate: string
  endDate: string
  isCurrent: boolean
  summary: string
  highlights: string[]
}

export interface Project {
  id: string
  name: string
  role: string
  startDate: string
  endDate: string
  link: string
  description: string
  techStack: string[]
  responsibilities: string[]
  achievements: string[]
  responsibilitiesText: string
  achievementsText: string
}

export interface SkillGroup {
  id: string
  category: string
  items: Array<{ name: string; level: SkillLevel }>
}

export interface Certificate {
  id: string
  name: string
  issuer: string
  date: string
  description: string
}

export interface CustomSection {
  id: string
  title: string
  items: Array<{
    id: string
    title: string
    subtitle: string
    startDate: string
    endDate: string
    description: string[]
  }>
}

export interface ResumeSettings {
  pageSize: 'A4'
  primaryColor: string
  fontFamily: string
  sectionOrder: ResumeSectionId[]
}
