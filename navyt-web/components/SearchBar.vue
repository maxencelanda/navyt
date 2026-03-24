<template>
  <div class="search-wrapper">
    <div class="search-box" :class="{ focused }">
      <span class="search-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
      </span>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Search YouTube…"
        @focus="focused = true"
        @blur="focused = false"
        @keydown.enter="emit('search', query)"
      />
      <button v-if="query" class="clear-btn" @click="query = ''; emit('clear')">×</button>
      <button class="search-btn" :disabled="!query.trim() || loading" @click="emit('search', query)">
        <span v-if="loading" class="spinner" />
        <span v-else>Search</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ loading?: boolean }>();
const emit = defineEmits<{
  search: [q: string];
  clear: [];
}>();

const query = ref("");
const focused = ref(false);
const inputRef = ref<HTMLInputElement>();
</script>

<style scoped>
.search-wrapper { width: 100%; max-width: 680px; margin: 0 auto; }

.search-box {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 4px;
  transition: border-color 0.15s, box-shadow 0.15s;
  overflow: hidden;
}
.search-box.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.search-icon {
  padding: 0 12px;
  color: var(--muted);
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  padding: 12px 0;
  outline: none;
}
input::placeholder { color: var(--muted); }

.clear-btn {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 1.3rem;
  padding: 0 8px;
  cursor: pointer;
  line-height: 1;
  transition: color 0.1s;
}
.clear-btn:hover { color: var(--text); }

.search-btn {
  background: var(--accent);
  color: #000;
  border: none;
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0 20px;
  height: 100%;
  min-height: 46px;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}
.search-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.search-btn:not(:disabled):hover { background: var(--accent-bright); }

.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid rgba(0,0,0,0.3);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>