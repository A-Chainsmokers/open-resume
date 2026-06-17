<script setup lang="ts">
const items = defineModel<string[]>({ required: true })

function addItem() {
  items.value.push('')
}

function removeItem(index: number) {
  items.value.splice(index, 1)
}
</script>

<template>
  <div class="text-list">
    <div v-for="(_, index) in items" :key="index" class="inline-row">
      <a-textarea v-model:value="items[index]" :rows="2" placeholder="输入一条描述" />
      <a-button danger @click="removeItem(index)">删除</a-button>
    </div>
    <a-button @click="addItem">添加描述</a-button>
  </div>
</template>
