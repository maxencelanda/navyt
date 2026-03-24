<template>
  <div class="results">
    <p v-if="results.length" class="count">
      {{ results.length }} results
    </p>
    <TransitionGroup name="list" tag="div" class="list">
      <VideoCard
        v-for="video in results"
        :key="video.id"
        :video="video"
        @select="emit('select', video)"
        @download="emit('download', video)"
      />
    </TransitionGroup>
    <div v-if="!results.length && !loading" class="empty">
      <span>No results yet — search something above</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ results: any[]; loading?: boolean }>();
const emit = defineEmits<{ select: [v: any]; download: [v: any] }>();
</script>

<style scoped>
.results { width: 100%; }

.count {
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  margin-bottom: 12px;
  letter-spacing: 0.04em;
}

.list { display: flex; flex-direction: column; gap: 8px; }

.list-move, .list-enter-active, .list-leave-active {
  transition: all 0.2s ease;
}
.list-enter-from { opacity: 0; transform: translateY(6px); }
.list-leave-to { opacity: 0; }

.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--muted);
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  border: 1px dashed var(--border);
  border-radius: 4px;
}
</style>