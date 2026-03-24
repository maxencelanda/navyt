<template>
  <aside class="queue" :class="{ open }">
    <div class="queue-header" @click="open = !open">
      <span class="label">Queue</span>
      <span v-if="jobs.length" class="badge">{{ jobs.length }}</span>
      <svg class="chevron" :class="{ rotated: open }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M18 15l-6-6-6 6"/>
      </svg>
    </div>

    <Transition name="slide">
      <div v-if="open" class="queue-body">
        <div v-if="!jobs.length" class="empty">No downloads yet</div>
        <TransitionGroup name="list" tag="div" class="job-list">
          <div v-for="job in jobs" :key="job.id" class="job">
            <div class="job-info">
              <p class="job-title">{{ job.title || job.video_id }}</p>
              <p v-if="job.artist" class="job-meta">{{ job.artist }}{{ job.album ? ` — ${job.album}` : '' }}</p>
            </div>
            <div class="job-right">
              <span class="status" :class="job.status">{{ job.status }}</span>
              <button class="remove-btn" @click="remove(job.id)">×</button>
            </div>
          </div>
        </TransitionGroup>
        <button v-if="jobs.length" class="clear-btn" @click="clearDone">Clear done</button>
      </div>
    </Transition>
  </aside>
</template>

<script setup lang="ts">
const { listDownloads, deleteJob } = useApi();

const open = ref(false);
const jobs = ref<any[]>([]);

const fetchJobs = async () => {
  jobs.value = await listDownloads();
};

const remove = async (id: string) => {
  await deleteJob(id);
  await fetchJobs();
};

const clearDone = async () => {
  const done = jobs.value.filter(j => j.status === "done" || j.status === "error");
  await Promise.all(done.map(j => deleteJob(j.id)));
  await fetchJobs();
};

// Poll while there are active jobs
let interval: ReturnType<typeof setInterval>;
watch(jobs, (val) => {
  const active = val.some(j => j.status === "queued" || j.status === "downloading");
  if (active && !interval) {
    interval = setInterval(fetchJobs, 2000);
  } else if (!active && interval) {
    clearInterval(interval);
    interval = undefined as any;
  }
});

onMounted(fetchJobs);
onBeforeUnmount(() => clearInterval(interval));

// Expose for parent to trigger refresh
defineExpose({ fetchJobs, open });
</script>

<style scoped>
.queue {
  position: fixed;
  bottom: 0; right: 24px;
  width: 340px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-bottom: none;
  border-radius: 6px 6px 0 0;
  z-index: 50;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
}

.queue-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
}

.label {
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.05em;
  flex: 1;
}

.badge {
  background: var(--accent);
  color: #000;
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
}

.chevron { color: var(--muted); transition: transform 0.2s; }
.chevron.rotated { transform: rotate(180deg); }

.queue-body { padding: 0 16px 16px; max-height: 300px; overflow-y: auto; }

.empty {
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
  padding: 20px 0;
}

.job-list { display: flex; flex-direction: column; gap: 6px; }

.job {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: var(--bg);
}

.job-info { flex: 1; min-width: 0; }
.job-title {
  font-size: 0.8rem; font-weight: 500; color: var(--text);
  margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-family: 'DM Sans', sans-serif;
}
.job-meta { font-size: 0.72rem; color: var(--muted); margin: 2px 0 0; }

.job-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.status {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: 700;
}
.status.queued { background: rgba(255,200,0,0.15); color: #ffc800; }
.status.downloading { background: rgba(0,160,255,0.15); color: #00a0ff; }
.status.done { background: rgba(0,220,120,0.15); color: #00dc78; }
.status.error { background: rgba(255,60,60,0.15); color: #ff3c3c; }

.remove-btn {
  background: none; border: none; color: var(--muted);
  font-size: 1.1rem; cursor: pointer; line-height: 1; padding: 0 2px;
}
.remove-btn:hover { color: var(--text); }

.clear-btn {
  margin-top: 10px;
  width: 100%;
  background: none;
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--muted);
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  padding: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.clear-btn:hover { border-color: var(--accent); color: var(--accent); }

.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from { opacity: 0; transform: translateY(10px); }
.slide-leave-to { opacity: 0; }
.list-enter-active, .list-leave-active { transition: all 0.2s; }
.list-enter-from { opacity: 0; transform: translateY(4px); }
.list-leave-to { opacity: 0; }
</style>