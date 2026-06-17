<script setup lang="ts">
import type { ResumeData } from '../types/resume'
import DynamicTemplate from './templates/DynamicTemplate.vue'
import { getTemplateDef } from '../utils/templates'

defineProps<{ resume: ResumeData }>()
</script>

<template>
  <DynamicTemplate :resume="resume" :def="getTemplateDef(resume.templateId)" />
</template>
