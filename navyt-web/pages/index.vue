<template>
  <div class="layout">
    <header class="site-header">
      <div class="logo">
        <span class="logo-mark">▶</span>
        <span class="logo-text">NAVYT</span>
      </div>
      <p class="tagline">YouTube → Navidrome</p>
    </header>

    <main class="main">
      <SearchBar :loading="searching" @search="doSearch" @clear="results = []" />

      <div v-if="searching" class="skeleton-list">
        <div v-for="i in 6" :key="i" class="skeleton" />
      </div>
      <SearchResults
        v-else
        :results="results"
        @select="openModal"
        @download="openModal"
      />
    </main>

    <DownloadModal
      :video="selectedVideo"
      @close="selectedVideo = null"
      @submitted="onJobSubmitted"
    />

    <DownloadQueue ref="queueRef" />
  </div>
</template>

<script setup lang="ts">
const { search } = useApi();

const results = ref<any[]>([]);
const searching = ref(false);
const selectedVideo = ref<any>(null);
const queueRef = ref<any>(null);

const doSearch = async (q: string) => {
  if (!q.trim()) return;
  searching.value = true;
  try {
    results.value = await search(q);
  } finally {
    searching.value = false;
  }
};

const openModal = (video: any) => {
  selectedVideo.value = video;
};

const onJobSubmitted = async () => {
  queueRef.value?.fetchJobs();
  queueRef.value && (queueRef.value.open = true);
};
</script>

<style>
/* ── Global tokens ── */
:root {
  --bg: #0d0d0d;
  --surface: #161616;
  --surface-hover: #1c1c1c;
  --border: #2a2a2a;
  --text: #e8e8e8;
  --muted: #666;
  --accent: #c8f135;
  --accent-bright: #d8ff4a;
  --accent-dim: rgba(200, 241, 53, 0.1);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
}

/* ── Layout ── */
.layout {
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 24px 120px;
}

.site-header {
  display: flex;
  align-items: baseline;
  gap: 20px;
  margin-bottom: 36px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  font-size: 1.1rem;
  color: var(--accent);
}

.logo-text {
  font-family: 'Space Mono', monospace;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.12em;
}

.tagline {
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.06em;
}

.main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Skeleton loading ── */
.skeleton-list { display: flex; flex-direction: column; gap: 8px; }
.skeleton {
  height: 103px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface-hover) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer { to { background-position: -200% 0; } }
</style>