<script setup lang="ts">
// A fake Jupyter cell: In [ ] → In [*] (running) → In [n] with output, on one click.
// Optional re-run: on the `rerun` click it runs again → In [rerunN] with the #rerun-output slot.
import { computed, onMounted, onUnmounted, ref, useSlots, watch } from 'vue'
import { useSlideContext } from '@slidev/client'

const props = withDefaults(defineProps<{
  n: number | string
  at?: number | string
  delay?: number
  label?: string
  rerun?: number | string
  rerunN?: number | string
}>(), { at: '+1', delay: 700 })

const slots = useSlots()
const { $clicksContext: clicks, $renderContext } = useSlideContext()
const id = `jupyter-cell-${Math.random().toString(36).slice(2)}`
// phase 0: never run, 1: first run, 2: re-run
const phase = ref(0)
const running = ref(false)
let timer: ReturnType<typeof setTimeout> | undefined

// Overview and thumbnails skip the animation and show the finished cell.
const animate = computed(() => ['slide', 'presenter'].includes($renderContext.value))
const hasRerun = computed(() => props.rerun != null)

function goTo(target: number) {
  clearTimeout(timer)
  if (target > phase.value && animate.value) {
    running.value = true
    timer = setTimeout(() => {
      running.value = false
      phase.value = target
    }, props.delay)
  }
  else {
    running.value = false
    phase.value = target
  }
}

onMounted(() => {
  const info = clicks.calculateSince(props.at, 1)
  if (!info) {
    phase.value = hasRerun.value ? 2 : 1
    return
  }
  clicks.register(id, info)
  const rerunInfo = hasRerun.value ? clicks.calculateSince(props.rerun!, 1) : null
  if (rerunInfo)
    clicks.register(`${id}-rerun`, rerunInfo)
  watch(
    () => [info.isActive.value, rerunInfo?.isActive.value ?? false],
    ([first, again]) => goTo(again ? 2 : first ? 1 : 0),
    { immediate: true },
  )
})

onUnmounted(() => {
  clearTimeout(timer)
  clicks.unregister(id)
  clicks.unregister(`${id}-rerun`)
})

const state = computed(() => running.value ? 'running' : phase.value > 0 ? 'done' : 'idle')
const prompt = computed(() => {
  if (running.value)
    return '*'
  return [' ', props.n, props.rerunN ?? props.n][phase.value]
})
const showRerunOutput = computed(() => phase.value === 2 && !!slots['rerun-output'])
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
      <div class="jc-output">
        <slot v-if="showRerunOutput" name="rerun-output" />
        <slot v-else name="output" />
      </div>
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
