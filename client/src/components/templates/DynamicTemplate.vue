<script setup lang="ts">
import type { ResumeData, ResumeSectionId } from '../../types/resume'
import type { TemplateDef } from '../../types/template'

defineProps<{
  resume: ResumeData
  def: TemplateDef
}>()

const defaultOrder: ResumeSectionId[] = ['profile', 'workExperience', 'projects', 'education', 'skills']

function sectionOrder(resume: ResumeData): ResumeSectionId[] {
  return resume.settings.sectionOrder ?? defaultOrder
}
</script>

<template>
  <!-- custom CSS injection -->
  <div v-if="def.css" v-html="`<style>${def.css}</style>`" style="display:none" />

  <article class="resume-page" :class="def.cssClass">

    <!-- ===== CENTER HEADER (classic) ===== -->
    <header v-if="def.layout === 'center'" class="resume-head image-format-head">
      <div class="head-copy">
        <h1>{{ resume.profile.name }}</h1>
        <p class="contact compact-contact">{{ resume.profile.gender }} | 年龄：{{ resume.profile.age }} | ✉ {{ resume.profile.email }}</p>
        <p class="contact compact-contact">{{ resume.profile.workYears }} | 求职意向：{{ resume.profile.headline }} | 期望薪资：{{ resume.profile.expectedSalary }} | 期望城市：{{ resume.profile.expectedCity || resume.profile.city }}</p>
      </div>
      <img v-if="resume.profile.avatar" class="avatar" :src="resume.profile.avatar" alt="头像" />
    </header>

    <!-- ===== COMPACT HEADER (minimal) ===== -->
    <header v-else-if="def.layout === 'compact'">
      <h1>{{ resume.profile.name }}</h1>
      <p>{{ resume.profile.headline }} / {{ resume.profile.phone }} / {{ resume.profile.email }} / {{ resume.profile.city }}</p>
    </header>

    <!-- ===== SIDEBAR (modern) ===== -->
    <aside v-if="def.layout === 'sidebar'">
      <h1>{{ resume.profile.name }}</h1>
      <p>{{ resume.profile.headline }}</p>
      <div class="side-block">
        <b>联系方式</b>
        <span>{{ resume.profile.phone }}</span>
        <span>{{ resume.profile.email }}</span>
        <span>{{ resume.profile.city }}</span>
      </div>
      <div v-if="def.sidebarSections.includes('skills') && resume.skills.length" class="side-block">
        <b>{{ def.labels.skills }}</b>
        <template v-for="group in resume.skills" :key="group.id">
          <em>{{ group.category }}</em>
          <span>{{ group.items.map(i => i.name).join(' / ') }}</span>
        </template>
      </div>
    </aside>

    <!-- ===== CONTENT WRAPPER (sidebar uses <main>, others render inline) ===== -->
    <main v-if="def.layout === 'sidebar'" class="content-body">
      <template v-for="sid in sectionOrder(resume)" :key="sid">
        <!-- PROFILE (sidebar → plain text) -->
        <section v-if="sid === 'profile' && resume.profile.summary">
          <h2>{{ def.labels.profile }}</h2>
          <p>{{ resume.profile.summary }}</p>
        </section>

        <!-- WORK EXPERIENCE -->
        <section v-else-if="sid === 'workExperience' && resume.workExperience.length">
          <h2>{{ def.labels.workExperience }}</h2>
          <div v-for="work in resume.workExperience" :key="work.id" class="item">
            <div class="item-title">
              <strong>{{ work.company }} · {{ work.position }}</strong>
              <span>{{ work.startDate }} - {{ work.isCurrent ? def.currentText : work.endDate }}</span>
            </div>
            <ul v-if="work.highlights?.length">
              <li v-for="line in work.highlights" :key="line">{{ line }}</li>
            </ul>
          </div>
        </section>

        <!-- PROJECTS (sidebar → combined list) -->
        <section v-else-if="sid === 'projects' && resume.projects.length">
          <h2>{{ def.labels.projects }}</h2>
          <div v-for="project in resume.projects" :key="project.id" class="item">
            <div class="item-title">
              <strong>{{ project.name }} · {{ project.role }}</strong>
              <span>{{ project.startDate }} - {{ project.endDate }}</span>
            </div>
            <p v-if="project.description">{{ project.description }}</p>
            <p v-if="project.techStack?.length">技术栈：{{ project.techStack.join(', ') }}</p>
            <ul v-if="(project.responsibilities?.length || project.achievements?.length)">
              <li v-for="line in [...(project.responsibilities || []), ...(project.achievements || [])]" :key="line">{{ line }}</li>
            </ul>
          </div>
        </section>

        <!-- EDUCATION (sidebar → simple) -->
        <section v-else-if="sid === 'education' && resume.education.length">
          <h2>{{ def.labels.education }}</h2>
          <div v-for="edu in resume.education" :key="edu.id" class="item">
            <strong>{{ edu.school }} · {{ edu.major }}</strong>
            <p>{{ edu.degree }} / {{ edu.startDate }} - {{ edu.endDate }}</p>
          </div>
        </section>
      </template>
    </main>

    <!-- ===== INLINE SECTIONS (center + compact layouts) ===== -->
    <template v-else v-for="sid in sectionOrder(resume)" :key="sid">
      <!-- PROFILE -->
      <section v-if="sid === 'profile' && resume.profile.summary">
        <h2>{{ def.labels.profile }}</h2>
        <div v-if="def.profileOutput === 'rich'" class="rich-output" v-html="resume.profile.summary" />
        <p v-else>{{ resume.profile.summary }}</p>
      </section>

      <!-- WORK EXPERIENCE -->
      <section v-else-if="sid === 'workExperience' && resume.workExperience.length">
        <h2>{{ def.labels.workExperience }}</h2>
        <div v-for="work in resume.workExperience" :key="work.id" class="item">
          <div class="item-title image-item-title">
            <template v-if="def.layout === 'compact'">
              <strong>{{ work.position }}, {{ work.company }}</strong>
              <span>{{ work.startDate }} - {{ work.isCurrent ? def.currentText : work.endDate }}</span>
            </template>
            <template v-else>
              <strong>{{ work.company }}</strong><span>{{ work.position }}</span>
              <time>{{ work.startDate }}-{{ work.isCurrent ? def.currentText : work.endDate }}</time>
            </template>
          </div>
          <div v-if="def.workOutput === 'rich' && work.summary" class="rich-output" v-html="work.summary" />
          <ul v-else-if="def.workOutput === 'highlights' && work.highlights?.length">
            <li v-for="line in work.highlights" :key="line">{{ line }}</li>
          </ul>
        </div>
      </section>

      <!-- PROJECTS -->
      <section v-else-if="sid === 'projects' && resume.projects.length">
        <h2>{{ def.labels.projects }}</h2>
        <div v-for="project in resume.projects" :key="project.id" class="item">
          <div v-if="def.projectsOutput !== 'compact'" class="item-title image-item-title">
            <strong>{{ project.name }}</strong><span>{{ project.role }}</span>
            <time>{{ project.startDate }}-{{ project.endDate }}</time>
          </div>
          <template v-if="def.projectsOutput === 'rich'">
            <p v-if="project.description">{{ project.description }}</p>
            <p v-if="project.techStack?.length" class="label-line">技术栈：{{ project.techStack.join('、') }}</p>
            <div v-if="project.responsibilitiesText">
              <p class="label-line">职责：</p>
              <div class="rich-output" v-html="project.responsibilitiesText" />
            </div>
            <div v-if="project.achievementsText">
              <p class="label-line">成果：</p>
              <div class="rich-output" v-html="project.achievementsText" />
            </div>
          </template>
          <template v-else-if="def.projectsOutput === 'list'">
            <p v-if="project.description">{{ project.description }}</p>
            <p v-if="project.techStack?.length">技术栈：{{ project.techStack.join(', ') }}</p>
            <ul v-if="(project.responsibilities?.length || project.achievements?.length)">
              <li v-for="line in [...(project.responsibilities || []), ...(project.achievements || [])]" :key="line">{{ line }}</li>
            </ul>
          </template>
          <template v-else>
            <div class="item-title image-item-title">
              <strong>{{ project.name }}</strong>
              <span>{{ project.techStack?.join(', ') || '' }}</span>
            </div>
            <p>{{ project.description }}</p>
          </template>
        </div>
      </section>

      <!-- EDUCATION -->
      <section v-else-if="sid === 'education' && resume.education.length">
        <h2>{{ def.labels.education }}</h2>
        <div v-for="edu in resume.education" :key="edu.id" class="item">
          <template v-if="def.educationOutput === 'detailed'">
            <div class="item-title image-item-title edu-title">
              <strong>{{ edu.school }}</strong><span>{{ edu.degree }}</span><span>{{ edu.major }}</span>
              <time>{{ edu.startDate }}-{{ edu.endDate }}</time>
            </div>
            <ul><li v-for="line in edu.description" :key="line">{{ line }}</li></ul>
          </template>
          <template v-else>
            <p>{{ edu.school }} · {{ edu.major }} · {{ edu.degree }}</p>
          </template>
        </div>
      </section>

      <!-- SKILLS -->
      <section v-else-if="sid === 'skills' && resume.skills.length">
        <h2>{{ def.labels.skills }}</h2>
        <p v-for="group in resume.skills" :key="group.id">
          <strong>{{ group.category }}：</strong>
          <template v-if="def.skillsOutput === 'with-level'">
            {{ group.items.map((item) => item.level ? `${item.name}(${item.level})` : item.name).join('、') }}
          </template>
          <template v-else>
            {{ group.items.map((item) => item.name).join(', ') }}
          </template>
        </p>
      </section>
    </template>

  </article>
</template>
