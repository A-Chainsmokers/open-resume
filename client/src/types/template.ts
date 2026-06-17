import type { ResumeSectionId } from './resume'

export type LayoutType = 'center' | 'sidebar' | 'compact'
export type SectionOutput = 'rich' | 'text' | 'highlights' | 'list' | 'compact' | 'detailed' | 'simple' | 'with-level' | 'flat'

export interface TemplateDef {
  id: string
  label: string
  cssClass: string
  css: string
  layout: LayoutType
  sidebarSections: string[]
  labels: Record<ResumeSectionId, string>
  currentText: string
  profileOutput: 'rich' | 'text'
  workOutput: 'rich' | 'highlights'
  projectsOutput: 'rich' | 'list' | 'compact'
  educationOutput: 'detailed' | 'simple'
  skillsOutput: 'with-level' | 'flat'
}
