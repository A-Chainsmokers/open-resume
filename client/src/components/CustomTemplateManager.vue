<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import type { TemplateDef } from '../types/template'
import { loadCustomTemplates, removeCustomTemplate, validateTemplateDef, addCustomTemplate } from '../utils/customTemplates'

const emit = defineEmits<{ changed: [] }>()

const customTemplates = ref<TemplateDef[]>(loadCustomTemplates())

function refresh() {
  customTemplates.value = loadCustomTemplates()
  emit('changed')
}

function handleImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const parsed = JSON.parse(String(reader.result))
      if (!validateTemplateDef(parsed)) {
        message.error('模板 JSON 格式不正确，请检查模板定义')
        return
      }
      const def = parsed as TemplateDef
      addCustomTemplate(def)
      message.success(`模板 "${def.label}" 导入成功`)
      refresh()
    } catch {
      message.error('JSON 解析失败')
    }
  }
  reader.readAsText(file)
  input.value = ''
}

function handleDelete(id: string) {
  removeCustomTemplate(id)
  message.info('自定义模板已删除')
  refresh()
}
</script>

<template>
  <section class="settings-section">
    <h3>自定义模板</h3>

    <div v-if="customTemplates.length" style="margin-bottom:12px">
      <div v-for="tpl in customTemplates" :key="tpl.id" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;padding:6px 10px;border:1px solid var(--app-line);border-radius:8px">
        <span style="flex:1;font-weight:600">{{ tpl.label }}</span>
        <small style="color:var(--app-muted)">({{ tpl.id }})</small>
        <a-button size="small" danger @click="handleDelete(tpl.id)">删除</a-button>
      </div>
    </div>
    <p v-else style="color:var(--app-muted);font-size:13px;margin:0 0 12px">暂无自定义模板</p>

    <span class="ant-file-button" style="display:inline-flex;margin-bottom:12px">
      <a-button>导入模板 JSON</a-button>
      <input type="file" accept=".json" @change="handleImport" />
    </span>

    <details style="font-size:13px;color:var(--app-muted);cursor:pointer;margin-top:6px">
      <summary style="font-weight:600;margin-bottom:6px">JSON 格式说明</summary>
      <pre style="background:rgba(0,0,0,.04);padding:10px;border-radius:8px;overflow-x:auto;font-size:12px;line-height:1.6;white-space:pre-wrap">{<br>  "id": "my-template",        // 唯一标识<br>  "label": "我的模板",         // 显示名称<br>  "cssClass": "my-template",   // CSS 类名（用于自行编写样式）<br>  "css": "",                   // 自定义 CSS 样式（可选，空字符串则不注入）<br>  "layout": "center",          // 布局：center | sidebar | compact<br>  "sidebarSections": [],       // 侧边栏显示的区块（如 ["skills"]）<br>  "labels": {                  // 各区块标题<br>    "profile": "个人优势",<br>    "workExperience": "工作经历",<br>    "projects": "项目经历",<br>    "education": "教育经历",<br>    "skills": "技能"<br>  },<br>  "currentText": "至今",       // 当前职位的日期显示文字<br>  "profileOutput": "rich",     // rich | text<br>  "workOutput": "rich",        // rich | highlights<br>  "projectsOutput": "rich",    // rich | list | compact<br>  "educationOutput": "detailed",// detailed | simple<br>  "skillsOutput": "with-level" // with-level | flat<br>}</pre>
    </details>

    <details style="font-size:13px;color:var(--app-muted);cursor:pointer;margin-top:8px">
      <summary style="font-weight:600;margin-bottom:6px">🤖 AI 生成提示词</summary>
      <div style="background:rgba(0,0,0,.04);padding:10px;border-radius:8px;white-space:pre-wrap;font-size:12px;line-height:1.6">将这段提示词发给 AI，让它帮你生成模板 JSON：

你是一个简历模板设计师。请根据以下模板定义格式，生成一份简历模板 JSON。

模板定义字段说明：
- id：唯一标识符，英文小写
- label：显示名称
- cssClass：CSS 类名，请使用与 id 相同的值
- css：自定义 CSS 样式，用于控制模板外观（字体、颜色、边距、布局等）。如不需要自定义样式则留空字符串
- layout：整体布局，center（居中头部+正文）、sidebar（侧边栏+主内容区）、compact（紧凑头部+正文）
- sidebarSections：放在侧边栏的区块名，layout 为 sidebar 时建议设为 ["skills"]
- labels：各章节标题，键名固定为 profile/workExperience/projects/education/skills
- currentText：当前职位的日期显示文字（中文用"至今"，英文用"Now"）
- profileOutput：个人优势输出方式，rich（富文本）、text（纯文本）
- workOutput：工作经历输出方式，rich（富文本描述）、highlights（要点列表）
- projectsOutput：项目经历输出方式，rich（详细含职责/成果富文本）、list（要点列表）、compact（精简）
- educationOutput：教育经历输出方式，detailed（详细含描述列表）、simple（简单一行）
- skillsOutput：技能输出方式，with-level（显示熟练度）、flat（仅名称）

请按以上格式生成一个 JSON 模板，风格为 [在此描述你想要的风格，如：简洁商务、蓝白配色、左侧栏深色、卡片式等]。</div>
    </details>
  </section>
</template>
