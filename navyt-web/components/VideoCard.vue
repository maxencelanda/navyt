<template>
  <div class="card" @click="emit('select', video)">
    <div class="thumb-wrap">
      <img :src="video.thumbnail" :alt="video.title" loading="lazy" />
      <span v-if="video.duration" class="duration">{{ formatDuration(video.duration) }}</span>
    </div>
    <div class="info">
      <p class="title">{{ video.title }}</p>
      <p class="channel">{{ video.channel }}</p>
      <p v-if="video.view_count" class="views">{{ formatViews(video.view_count) }} views</p>
    </div>
    <button class="dl-btn" @click.stop="emit('download', video)">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 3v13M7 11l5 5 5-5"/><path d="M5 21h14"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ video: any }>();
const emit = defineEmits<{ select: [v: any]; download: [v: any] }>();

const formatDuration = (secs: number) => {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
};

const formatViews = (n: number) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return n.toString();
};
</script>

<style scoped>
.card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--surface);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  position: relative;
}
.card:hover { border-color: var(--accent); background: var(--surface-hover); }

.thumb-wrap {
  position: relative;
  flex-shrink: 0;
  width: 140px;
  height: 79px;
  border-radius: 2px;
  overflow: hidden;
  background: var(--bg);
}
.thumb-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }

.duration {
  position: absolute;
  bottom: 4px; right: 4px;
  background: rgba(0,0,0,0.8);
  color: #fff;
  font-family: 'Space Mono', monospace;
  font-size: 0.7rem;
  padding: 1px 5px;
  border-radius: 2px;
}

.info { flex: 1; min-width: 0; }

.title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.channel {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 2px;
  font-family: 'DM Sans', sans-serif;
}

.views {
  font-size: 0.73rem;
  color: var(--muted);
  margin: 0;
  font-family: 'Space Mono', monospace;
}

.dl-btn {
  flex-shrink: 0;
  width: 32px; height: 32px;
  border-radius: 3px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  margin-top: 2px;
}
.dl-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
</style>