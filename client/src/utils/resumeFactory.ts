import type { ResumeData, ResumeSectionId } from '../types/resume'

const now = () => new Date().toISOString()
const id = (prefix: string) => `${prefix}_${Math.random().toString(36).slice(2, 9)}`
export const defaultSectionOrder: ResumeSectionId[] = ['profile', 'workExperience', 'projects', 'education', 'skills']

export function createDefaultResume(): ResumeData {
  return {
    schemaVersion: '1.0.0',
    id: id('resume'),
    title: '前端工程师简历',
    templateId: 'classic',
    language: 'zh-CN',
    createdAt: now(),
    updatedAt: now(),
    profile: {
      name: '张三',
      headline: '前端工程师',
      phone: '13800000000',
      email: 'zhangsan@example.com',
      city: '上海',
      gender: '男',
      age: '26岁',
      workYears: '5年工作经验',
      expectedSalary: '13-14K',
      expectedCity: '济南',
      avatar: '',
      website: 'https://example.com',
      github: 'https://github.com/example',
      summary: '3 年前端开发经验，熟悉 Vue3、TypeScript、工程化和性能优化，具备从 0 到 1 搭建业务系统的经验。'
    },
    education: [{ id: id('edu'), school: '上海交通大学', degree: '本科', major: '计算机科学与技术', startDate: '2018-09', endDate: '2022-06', description: ['主修课程：数据结构、操作系统、计算机网络、数据库系统', '获得校级二等奖学金'] }],
    workExperience: [{ id: id('work'), company: '某互联网科技有限公司', position: '前端工程师', city: '上海', startDate: '2022-07', endDate: '2025-04', isCurrent: false, summary: '负责企业级 SaaS 后台系统的前端开发与工程化建设。', highlights: ['基于 Vue3 和 TypeScript 负责核心业务模块开发。', '优化首屏加载性能，将核心页面加载时间从 3.2s 降低至 1.6s。'] }],
    projects: [{ id: id('project'), name: '在线数据分析平台', role: '前端负责人', startDate: '2024-01', endDate: '2024-09', link: 'https://example.com/project', description: '面向企业用户的数据可视化与报表分析平台。', techStack: ['Vue3', 'TypeScript', 'Vite', 'Pinia', 'ECharts'], responsibilities: ['负责项目整体前端架构设计和核心模块开发。', '封装图表配置系统，支持多类型图表快速生成。'], achievements: ['将报表配置效率提升约 50%。'], responsibilitiesText: '<ol><li>负责项目整体前端架构设计和核心模块开发。</li><li>封装图表配置系统，支持多类型图表快速生成。</li></ol>', achievementsText: '<ol><li>将报表配置效率提升约 50%。</li></ol>' }],
    skills: [{ id: id('skill'), category: '前端开发', items: [{ name: 'Vue3', level: '熟练' }, { name: 'TypeScript', level: '熟练' }, { name: 'Vite', level: '熟悉' }] }],
    certificates: [{ id: id('cert'), name: '大学英语六级', issuer: '教育部考试中心', date: '2020-12', description: 'CET-6' }],
    customSections: [],
    settings: { pageSize: 'A4', primaryColor: '#22312f', fontFamily: 'Noto Serif SC, Songti SC, SimSun, serif', sectionOrder: [...defaultSectionOrder] }
  }
}

export function createId(prefix: string) {
  return id(prefix)
}
