<script setup lang="ts">
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import { shallowRef, onBeforeUnmount, ref, watch } from 'vue'

const model = defineModel<string>({ required: true })
const emit = defineEmits<{ changed: [] }>()
const editorRef = shallowRef<IDomEditor | undefined>()
const html = ref(model.value || '')

const toolbarConfig: Partial<IToolbarConfig> = {
  toolbarKeys: ['bold', 'italic', 'underline', '|', 'numberedList', 'bulletedList', '|', 'undo', 'redo']
}

const editorConfig: Partial<IEditorConfig> = {
  placeholder: '请输入内容...',
  readOnly: false,
  MENU_CONF: {}
}

function handleCreated(editor: IDomEditor) {
  editorRef.value = editor
}

function handleChange(editor: IDomEditor) {
  html.value = editor.getHtml()
  emit('changed')
}

watch(
  () => model.value,
  (value) => {
    if (value !== html.value) html.value = value || ''
  }
)

watch(html, (value) => {
  if (value !== model.value) model.value = value
})

onBeforeUnmount(() => {
  editorRef.value?.destroy()
})
</script>

<template>
  <div class="rich-text-wrap wang-rich-text">
    <Toolbar :editor="editorRef" :defaultConfig="toolbarConfig" mode="simple" />
    <Editor v-model="html" :defaultConfig="editorConfig" mode="simple" class="rich-editor" @onCreated="handleCreated" @onChange="handleChange" />
  </div>
</template>
