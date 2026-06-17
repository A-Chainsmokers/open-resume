import type { ResumeData } from '../types/resume'

export interface DiffEntry {
  section: string
  field: string
  oldValue: string
  newValue: string
}

const SECTION_LABELS: Record<string, string> = {
  title: '标题',
  templateId: '模板',
  language: '语言',
  profile: '基本信息',
  education: '教育经历',
  workExperience: '工作经历',
  projects: '项目经历',
  skills: '技能',
  certificates: '证书',
  customSections: '自定义模块',
  settings: '设置',
}

const FIELD_LABELS: Record<string, string> = {
  name: '名称',
  headline: '求职意向',
  phone: '手机号',
  email: '邮箱',
  city: '城市',
  gender: '性别',
  age: '年龄',
  workYears: '工作年限',
  expectedSalary: '期望薪资',
  expectedCity: '期望城市',
  avatar: '头像',
  website: '个人网站',
  github: 'GitHub',
  summary: '个人优势',
  school: '学校',
  degree: '学历',
  major: '专业',
  startDate: '开始时间',
  endDate: '结束时间',
  description: '描述',
  company: '公司',
  position: '职位',
  isCurrent: '至今',
  highlights: '亮点',
  role: '角色',
  link: '链接',
  techStack: '技术栈',
  responsibilities: '职责',
  achievements: '成果',
  responsibilitiesText: '职责',
  achievementsText: '成果',
  category: '分类',
  items: '技能项',
  level: '熟练度',
  issuer: '颁发机构',
  date: '日期',
  pageSize: '页面大小',
  primaryColor: '主题色',
  fontFamily: '字体',
  sectionOrder: '模块顺序',
}

const IGNORED_KEYS = new Set(['id', 'createdAt', 'updatedAt', 'schemaVersion'])

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value)
}

function cleanText(value: unknown): string {
  if (value == null || value === '') return '(空)'
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (Array.isArray(value)) return value.map(cleanText).join('，') || '(空)'
  if (typeof value === 'object') return JSON.stringify(value)
  const text = String(value).replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
  return text || '(空)'
}

function short(value: unknown, max = 80): string {
  const text = cleanText(value)
  return text.length <= max ? text : text.slice(0, max) + '...'
}

function sameValue(a: unknown, b: unknown): boolean {
  return JSON.stringify(a ?? null) === JSON.stringify(b ?? null)
}

function sectionLabel(path: string[]): string {
  return SECTION_LABELS[path[0]] ?? '其他'
}

function fieldLabel(path: string[]): string {
  const parts = path.slice(1).filter((part) => !IGNORED_KEYS.has(part))
  if (!parts.length) return SECTION_LABELS[path[0]] ?? path[0]
  return parts
    .map((part) => {
      if (/^\d+$/.test(part)) return `#${Number(part) + 1}`
      return FIELD_LABELS[part] ?? part
    })
    .join(' / ')
}

function walk(oldValue: unknown, newValue: unknown, path: string[], result: DiffEntry[]) {
  const key = path[path.length - 1]
  if (IGNORED_KEYS.has(key)) return
  if (sameValue(oldValue, newValue)) return

  if (Array.isArray(oldValue) || Array.isArray(newValue)) {
    const oldList = Array.isArray(oldValue) ? oldValue : []
    const newList = Array.isArray(newValue) ? newValue : []
    const max = Math.max(oldList.length, newList.length)
    for (let i = 0; i < max; i++) {
      walk(oldList[i], newList[i], [...path, String(i)], result)
    }
    return
  }

  if (isPlainObject(oldValue) || isPlainObject(newValue)) {
    const keys = new Set([
      ...Object.keys(isPlainObject(oldValue) ? oldValue : {}),
      ...Object.keys(isPlainObject(newValue) ? newValue : {}),
    ])
    for (const childKey of keys) {
      walk(
        isPlainObject(oldValue) ? oldValue[childKey] : undefined,
        isPlainObject(newValue) ? newValue[childKey] : undefined,
        [...path, childKey],
        result,
      )
    }
    return
  }

  result.push({
    section: sectionLabel(path),
    field: fieldLabel(path),
    oldValue: short(oldValue),
    newValue: short(newValue),
  })
}

export function diffResume(oldData: ResumeData, newData: ResumeData): DiffEntry[] {
  const result: DiffEntry[] = []
  const keys = new Set([...Object.keys(oldData), ...Object.keys(newData)])
  for (const key of keys) {
    walk(oldData[key as keyof ResumeData], newData[key as keyof ResumeData], [key], result)
  }
  return result
}
