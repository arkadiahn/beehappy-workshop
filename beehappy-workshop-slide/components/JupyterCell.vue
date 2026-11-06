<script setup lang="ts">
// A fake Jupyter cell: In [ ] → In [*] (running) → In [n] with output, on one click.
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useSlideContext } from '@slidev/client'

const props = withDefaults(defineProps<{
  n: number | string
  at?: number | string
  delay?: number
  label?: string
}>(), { at: '+1', delay: 700 })

const { $clicksContext: clicks, $renderContext } = useSlideContext()
const id = `jupyter-cell-${Math.random().toString(36).slice(2)}`
const active = ref(false)
const state = ref<'idle' | 'running' | 'done'>('idle')
let timer: ReturnType<typeof setTimeout> | undefined

// Overview and thumbnails skip the animation and show the finished cell.
const animate = computed(() => ['slide', 'presenter'].includes($renderContext.value))

onMounted(() => {
  const info = clicks.calculateSince(props.at, 1)
  if (!info) {
    state.value = 'done'
    return
  }
  clicks.register(id, info)
  watch(info.isActive, (isActive) => {
    clearTimeout(timer)
    if (!isActive) {
      state.value = 'idle'
    }
    else if (animate.value) {
      state.value = 'running'
      timer = setTimeout(() => { state.value = 'done' }, props.delay)
    }
    else {
      state.value = 'done'
    }
  }, { immediate: true })
})

onUnmounted(() => {
  clearTimeout(timer)
  clicks.unregister(id)
})

const prompt = computed(() => ({ idle: ' ', running: '*', done: props.n })[state.value])
</script>

<template>
  <div class="jc" :class="`jc-${state}`">
    <div v-if="label" class="jc-label">{{ label }}</div>
    <div class="jc-row">
      <div class="jc-prompt">In [{{ prompt }}]:</div>
      <div class="jc-input"><slot /></div>
    </div>
    <div class="jc-row jc-out-row">
      <div class="jc-prompt" />
      <div class="jc-output"><slot name="output" /></div>
    </div>
  </div>
</template>

<style scoped>
.jc { margin: 0.4rem 0; }
.jc-label {
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--bh-honey-600);
  margin-left: 4.2rem;
}
.jc-row { display: flex; align-items: flex-start; gap: 0.5rem; }
.jc-prompt {
  flex: 0 0 3.7rem;
  text-align: right;
  font-family: var(--slidev-code-font-family, monospace);
  font-size: 0.64rem;
  color: var(--bh-honey-700);
  padding-top: 0.55rem;
}
.jc-running .jc-prompt:first-child { animation: jc-pulse 0.6s ease-in-out infinite alternate; }
.jc-input {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--bh-honey-200);
  border-left: 3px solid var(--bh-honey-200);
  border-radius: 0.4rem;
  overflow: hidden;
  transition: border-color 0.2s;
}
.jc-running .jc-input { border-left-color: var(--bh-honey-500); }
.jc-input :deep(.slidev-code-wrapper),
.jc-input :deep(pre) { margin: 0 !important; border-radius: 0 !important; }
.jc-output {
  flex: 1;
  min-width: 0;
  font-family: var(--slidev-code-font-family, monospace);
  font-size: 0.64rem;
  line-height: 1.35;
  white-space: pre;
  color: var(--bh-ink-2);
  padding: 0.3rem 0.7rem 0;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 0.3s, transform 0.3s;
}
.jc-output :deep(pre) { margin: 0; font: inherit; background: none; }
.jc-done .jc-output { opacity: 1; transform: none; }
@keyframes jc-pulse { from { opacity: 1; } to { opacity: 0.35; } }
</style>
