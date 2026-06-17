<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { polishText } from '../../api/ai'
import type { ResumeData, ResumeSectionId } from '../../types/resume'
import { createId } from '../../utils/resumeFactory'
import MonthSelect from './MonthSelect.vue'
import RichTextEditor from './RichTextEditor.vue'
import TextListEditor from './TextListEditor.vue'

const resume = defineModel<ResumeData>({ required: true })
const emit = defineEmits<{ changed: [] }>()
const polishingKey = ref('')

function markChanged() {
  emit('changed')
}

function addEducation() {
  resume.value.education.push({ id: createId('edu'), school: '', degree: '', major: '', startDate: '', endDate: '', description: [''] })
  markChanged()
}

function addWork() {
  resume.value.workExperience.push({ id: createId('work'), company: '', position: '', city: '', startDate: '', endDate: '', isCurrent: false, summary: '', highlights: [''] })
  markChanged()
}

function addProject() {
  resume.value.projects.unshift({ id: createId('project'), name: '', role: '', startDate: '', endDate: '', link: '', description: '', techStack: [], responsibilities: [''], achievements: [''], responsibilitiesText: '', achievementsText: '' })
  markChanged()
}

function addSkillGroup() {
  resume.value.skills.push({ id: createId('skill'), category: '', items: [{ name: '', level: '' }] })
  markChanged()
}

function reorder<T>(items: T[], fromIndex: number, direction: -1 | 1) {
  const next = [...items]
  const toIndex = fromIndex + direction
  if (toIndex < 0 || toIndex >= next.length) return next
  const [item] = next.splice(fromIndex, 1)
  next.splice(toIndex, 0, item)
  return next
}

function moveEducation(index: number, direction: -1 | 1) {
  resume.value.education = reorder(resume.value.education, index, direction)
  markChanged()
}

function moveWork(index: number, direction: -1 | 1) {
  resume.value.workExperience = reorder(resume.value.workExperience, index, direction)
  markChanged()
}

function moveProject(index: number, direction: -1 | 1) {
  resume.value.projects = reorder(resume.value.projects, index, direction)
  markChanged()
}

function moveSkillGroup(index: number, direction: -1 | 1) {
  resume.value.skills = reorder(resume.value.skills, index, direction)
  markChanged()
}

const sectionNames: Record<ResumeSectionId, string> = {
  profile: '基本信息',
  education: '教育经历',
  workExperience: '工作经历',
  projects: '项目经历',
  skills: '技能'
}

function moveSection(index: number, direction: -1 | 1) {
  resume.value.settings.sectionOrder = reorder(resume.value.settings.sectionOrder, index, direction)
  markChanged()
}

function removeItem<T>(items: T[], index: number) {
  items.splice(index, 1)
  markChanged()
}

function splitTags(value: string) {
  return value.split(/[，,]/).map((item) => item.trim()).filter(Boolean)
}

async function polishField(key: string, field: string, html: string, apply: (html: string) => void, context?: Record<string, unknown>) {
  if (!html.trim()) {
    message.warning('请先输入需要润色的内容')
    return
  }

  polishingKey.value = key
  try {
    const result = await polishText({ field, html, context })
    apply(result.html)
    markChanged()
  } catch (error) {
    message.error(error instanceof Error ? error.message : 'AI 润色失败')
  } finally {
    polishingKey.value = ''
  }
}
</script>

<template>
  <a-form class="editor-form" layout="vertical" @input="$emit('changed')" @change="$emit('changed')">
    <a-card v-for="(sectionId, sectionIndex) in resume.settings.sectionOrder" :id="`resume-section-${sectionId}`" :key="sectionId" class="panel open-panel" :bordered="false">
      <template #title>{{ sectionNames[sectionId] }}</template>
      <template #extra>
        <a-space wrap>
          <a-button size="small" :disabled="sectionIndex === 0" @click.stop="moveSection(sectionIndex, -1)">模块上移</a-button>
          <a-button size="small" :disabled="sectionIndex === resume.settings.sectionOrder.length - 1" @click.stop="moveSection(sectionIndex, 1)">模块下移</a-button>
          <a-button v-if="sectionId === 'education'" size="small" type="primary" @click="addEducation">新增</a-button>
          <a-button v-if="sectionId === 'workExperience'" size="small" type="primary" @click="addWork">新增</a-button>
          <a-button v-if="sectionId === 'projects'" size="small" type="primary" @click="addProject">新增</a-button>
          <a-button v-if="sectionId === 'skills'" size="small" type="primary" @click="addSkillGroup">新增分类</a-button>
        </a-space>
      </template>

      <template v-if="sectionId === 'profile'">
        <div class="grid-2">
          <a-form-item label="姓名"><a-input v-model:value="resume.profile.name" /></a-form-item>
          <a-form-item label="求职意向"><a-input v-model:value="resume.profile.headline" /></a-form-item>
          <a-form-item label="性别"><a-input v-model:value="resume.profile.gender" /></a-form-item>
          <a-form-item label="年龄"><a-input v-model:value="resume.profile.age" placeholder="26岁" /></a-form-item>
          <a-form-item label="手机号"><a-input v-model:value="resume.profile.phone" /></a-form-item>
          <a-form-item label="邮箱"><a-input v-model:value="resume.profile.email" /></a-form-item>
          <a-form-item label="城市"><a-input v-model:value="resume.profile.city" /></a-form-item>
          <a-form-item label="工作年限"><a-input v-model:value="resume.profile.workYears" placeholder="5年工作经验" /></a-form-item>
          <a-form-item label="期望薪资"><a-input v-model:value="resume.profile.expectedSalary" placeholder="13-14K" /></a-form-item>
          <a-form-item label="期望城市"><a-input v-model:value="resume.profile.expectedCity" /></a-form-item>
        </div>
        <a-form-item label="头像图片地址"><a-input v-model:value="resume.profile.avatar" placeholder="https://..." /></a-form-item>
        <a-form-item label="个人网站"><a-input v-model:value="resume.profile.website" /></a-form-item>
        <a-form-item label="GitHub"><a-input v-model:value="resume.profile.github" /></a-form-item>
        <div class="field-block"><span>个人优势</span><a-button class="ai-button" size="small" :loading="polishingKey === 'profile-summary'" @click="polishField('profile-summary', '基本信息-个人优势', resume.profile.summary, (html) => resume.profile.summary = html, { headline: resume.profile.headline })">AI 润色</a-button><RichTextEditor v-model="resume.profile.summary" @changed="markChanged" /></div>
      </template>

      <template v-if="sectionId === 'education'">
        <a-card v-for="(edu, index) in resume.education" :key="edu.id" class="card-editor" size="small">
        <template #extra><a-space><a-button size="small" :disabled="index === 0" @click.stop="moveEducation(index, -1)">上移</a-button><a-button size="small" :disabled="index === resume.education.length - 1" @click.stop="moveEducation(index, 1)">下移</a-button><a-button size="small" danger @click="removeItem(resume.education, index)">删除</a-button></a-space></template>
        <div class="grid-2">
          <a-form-item label="学校"><a-input v-model:value="edu.school" /></a-form-item>
          <a-form-item label="专业"><a-input v-model:value="edu.major" /></a-form-item>
          <a-form-item label="学历"><a-input v-model:value="edu.degree" /></a-form-item>
          <a-form-item label="开始时间"><MonthSelect v-model="edu.startDate" /></a-form-item>
          <a-form-item label="结束时间"><MonthSelect v-model="edu.endDate" /></a-form-item>
        </div>
        <TextListEditor v-model="edu.description" />
      </a-card>
      </template>

      <template v-if="sectionId === 'workExperience'">
        <a-card v-for="(work, index) in resume.workExperience" :key="work.id" class="card-editor" size="small">
        <template #extra><a-space><a-button size="small" :disabled="index === 0" @click.stop="moveWork(index, -1)">上移</a-button><a-button size="small" :disabled="index === resume.workExperience.length - 1" @click.stop="moveWork(index, 1)">下移</a-button><a-button size="small" danger @click="removeItem(resume.workExperience, index)">删除</a-button></a-space></template>
        <div class="grid-2">
          <a-form-item label="公司"><a-input v-model:value="work.company" /></a-form-item>
          <a-form-item label="职位"><a-input v-model:value="work.position" /></a-form-item>
          <a-form-item label="城市"><a-input v-model:value="work.city" /></a-form-item>
          <a-form-item label="开始时间"><MonthSelect v-model="work.startDate" /></a-form-item>
          <a-form-item label="结束时间"><MonthSelect v-model="work.endDate" /></a-form-item>
        </div>
        <a-checkbox v-model:checked="work.isCurrent">至今</a-checkbox>
        <div class="field-block"><span>概述</span><a-button class="ai-button" size="small" :loading="polishingKey === `work-${work.id}`" @click="polishField(`work-${work.id}`, '工作经历-概述', work.summary, (html) => work.summary = html, { company: work.company, position: work.position })">AI 润色</a-button><RichTextEditor v-model="work.summary" @changed="markChanged" /></div>
      </a-card>
      </template>

      <template v-if="sectionId === 'projects'">
        <a-card v-for="(project, index) in resume.projects" :key="project.id" class="card-editor" size="small">
        <template #extra><a-space><a-button size="small" :disabled="index === 0" @click.stop="moveProject(index, -1)">上移</a-button><a-button size="small" :disabled="index === resume.projects.length - 1" @click.stop="moveProject(index, 1)">下移</a-button><a-button size="small" danger @click="removeItem(resume.projects, index)">删除</a-button></a-space></template>
        <div class="grid-2">
          <a-form-item label="项目名称"><a-input v-model:value="project.name" /></a-form-item>
          <a-form-item label="角色"><a-input v-model:value="project.role" /></a-form-item>
          <a-form-item label="开始时间"><MonthSelect v-model="project.startDate" /></a-form-item>
          <a-form-item label="结束时间"><MonthSelect v-model="project.endDate" /></a-form-item>
        </div>
        <a-form-item label="项目链接"><a-input v-model:value="project.link" /></a-form-item>
        <a-form-item label="项目描述"><a-textarea v-model:value="project.description" :rows="2" /></a-form-item>
        <a-form-item label="技术栈，用逗号分隔"><a-input :value="project.techStack.join('，')" @input="project.techStack = splitTags(($event.target as HTMLInputElement).value)" /></a-form-item>
        <div class="field-block"><span>职责</span><a-button class="ai-button" size="small" :loading="polishingKey === `project-duty-${project.id}`" @click="polishField(`project-duty-${project.id}`, '项目经历-职责', project.responsibilitiesText, (html) => project.responsibilitiesText = html, { name: project.name, role: project.role })">AI 润色</a-button><RichTextEditor v-model="project.responsibilitiesText" @changed="markChanged" /></div>
        <div class="field-block"><span>成果</span><a-button class="ai-button" size="small" :loading="polishingKey === `project-result-${project.id}`" @click="polishField(`project-result-${project.id}`, '项目经历-成果', project.achievementsText, (html) => project.achievementsText = html, { name: project.name, role: project.role })">AI 润色</a-button><RichTextEditor v-model="project.achievementsText" @changed="markChanged" /></div>
      </a-card>
      </template>

      <template v-if="sectionId === 'skills'">
        <a-card v-for="(group, groupIndex) in resume.skills" :key="group.id" class="card-editor" size="small">
        <template #extra><a-space><a-button size="small" :disabled="groupIndex === 0" @click.stop="moveSkillGroup(groupIndex, -1)">上移</a-button><a-button size="small" :disabled="groupIndex === resume.skills.length - 1" @click.stop="moveSkillGroup(groupIndex, 1)">下移</a-button><a-button size="small" danger @click="removeItem(resume.skills, groupIndex)">删除</a-button></a-space></template>
        <a-form-item label="分类"><a-input v-model:value="group.category" /></a-form-item>
        <div v-for="(skill, skillIndex) in group.items" :key="skillIndex" class="inline-row">
          <a-input v-model:value="skill.name" placeholder="技能名称" />
          <a-select v-model:value="skill.level" style="width: 110px"><a-select-option value="">不显示</a-select-option><a-select-option value="了解">了解</a-select-option><a-select-option value="熟悉">熟悉</a-select-option><a-select-option value="熟练">熟练</a-select-option><a-select-option value="精通">精通</a-select-option></a-select>
          <a-button danger @click="removeItem(group.items, skillIndex)">删除</a-button>
        </div>
        <a-button @click="group.items.push({ name: '', level: '' }); markChanged()">添加技能</a-button>
      </a-card>
      </template>
    </a-card>
  </a-form>
</template>
