<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="video" class="overlay" @click.self="emit('close')">
        <div class="modal">
          <button class="close" @click="emit('close')">×</button>
          <div class="header">
            <div class="embed-wrap">
                <iframe
                :src="`https://www.youtube.com/embed/${video.id}?autoplay=0`"
                frameborder="0"
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                />
            </div>
            <div>
                <p class="video-title">{{ video.title }}</p>
                <p class="channel">{{ video.channel }}</p>
            </div>
          </div>

          <!-- Deezer preview -->
          <Transition name="fade">
            <div v-if="mbPreview" class="mb-preview" :class="{ found: mbPreview.found }">
                <img v-if="mbPreview.found && mbPreview.cover_url" :src="mbPreview.cover_url" class="dz-thumb" />
                <span class="mb-icon">{{ mbPreview.found ? '✦' : '○' }}</span>
                <span v-if="mbPreview.found" class="dz-info">
                    Deezer match — <strong>{{ mbPreview.artist }}</strong>
                    · {{ mbPreview.album }}
                    <em v-if="mbPreview.year">({{ mbPreview.year }})</em>
                </span>
                <span v-else>No Deezer match found, using provided metadata</span>
                <button v-if="mbPreview.found" class="fill-btn" @click="fillFromDeezer">
                    ↙ Fill
                </button>
            </div>
          </Transition>

          <div class="fields">
            <label>
              <span>Title</span>
              <input v-model="form.title" type="text" :placeholder="video.title" @input="debouncedLookup" />
            </label>
            <label>
              <span>Artist</span>
              <input v-model="form.artist" type="text" placeholder="Artist name" @input="debouncedLookup" />
            </label>
            <label>
              <span>Album</span>
              <input v-model="form.album" type="text" placeholder="Album name" />
            </label>
          </div>

          <p class="hint">
            Saved to <code>{{ previewPath }}</code>
          </p>

          <button class="confirm-btn" :disabled="submitting" @click="submit">
            <span v-if="submitting" class="spinner" />
            <span v-else>Download as MP3</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = defineProps<{ video: any | null }>();
const emit = defineEmits<{ close: []; submitted: [job: any] }>();

const { startDownload } = useApi();
const config = useRuntimeConfig();

const form = reactive({ title: "", artist: "", album: "" });
const submitting = ref(false);
const mbPreview = ref<any>(null);
let lookupTimeout: ReturnType<typeof setTimeout>;

const sanitize = (s: string) => s.replace(/[^a-zA-Z0-9 .\-_()\[\]]/g, "_").trim();

const previewPath = computed(() => {
  const artist = sanitize(form.artist || "Unknown Artist");
  const album = sanitize(form.album || "Unknown Album");
  const title = sanitize(form.title || props.video?.title || "track");
  return `<MEDIA_DIR>/${artist}/${album}/${title}.mp3`;
});

const fillFromDeezer = () => {
  if (!mbPreview.value?.found) return;
  form.title  = mbPreview.value.title  || form.title;
  form.artist = mbPreview.value.artist || form.artist;
  form.album  = mbPreview.value.album  || form.album;
};

const lookupDeezer = async () => {
  const title = form.title || props.video?.title;
  const artist = form.artist || props.video?.channel;
  if (!title) return;

  try {
    const params = new URLSearchParams({ title, ...(artist ? { artist } : {}) });
    const data = await $fetch<any>(
      `${config.public.apiBase}/api/search/deezer?${params}`
    );
    mbPreview.value = data.found
    ? {
      found: true,
      title: data.title,
      artist: data.artist,
      album: data.album,
      year: data.year,
      cover_url: data.cover_url,
    }
    : { found: false };
  } catch {
    mbPreview.value = null;
  }
};

const debouncedLookup = () => {
  clearTimeout(lookupTimeout);
  lookupTimeout = setTimeout(lookupDeezer, 600);
};

watch(() => props.video, (v) => {
  if (v) {
    form.title = "";
    form.artist = "";
    form.album = "";
    mbPreview.value = null;
    submitting.value = false;
    setTimeout(lookupDeezer, 300);
  }
});

const submit = async () => {
  if (!props.video) return;
  submitting.value = true;
  try {
    const job = await startDownload({
      video_id: props.video.id,
      title: form.title || undefined,
      artist: form.artist || undefined,
      album: form.album || undefined,
    });
    emit("submitted", job);
    emit("close");
  } catch (e) {
    console.error(e);
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.modal {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 6px;
  padding: 24px;
  width: 100%;
  max-width: 480px;
  position: relative;
}

.close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; color: var(--muted);
  font-size: 1.4rem; cursor: pointer; line-height: 1;
}
.close:hover { color: var(--text); }

.header {
  display: flex; gap: 14px; align-items: flex-start;
  margin-bottom: 16px;
}
.embed-wrap {
  flex-shrink: 0;
  width: 160px;
  height: 90px;
  border-radius: 3px;
  overflow: hidden;
  background: var(--bg);
}
.embed-wrap iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

.video-title {
  font-size: 0.88rem; font-weight: 500; color: var(--text);
  margin: 0 0 4px; font-family: 'DM Sans', sans-serif;
}
.channel { font-size: 0.78rem; color: var(--muted); margin: 0; }

.dz-thumb {
  width: 32px; height: 32px;
  border-radius: 2px;
  object-fit: cover;
  flex-shrink: 0;
}

.dz-info { flex: 1; }

.fill-btn {
  flex-shrink: 0;
  background: var(--accent);
  color: #000;
  border: none;
  border-radius: 2px;
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 8px;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.fill-btn:hover { background: var(--accent-bright); }

.mb-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 3px;
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  margin-bottom: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  color: var(--muted);
}
.mb-preview.found {
  border-color: var(--accent);
  color: var(--text);
  background: var(--accent-dim);
}
.mb-preview strong { color: var(--accent); }
.mb-icon { font-size: 0.8rem; color: var(--accent); flex-shrink: 0; }

.fields { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }

label { display: flex; flex-direction: column; gap: 5px; }
label span {
  font-family: 'Space Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
label input {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  padding: 8px 10px;
  outline: none;
  transition: border-color 0.15s;
}
label input:focus { border-color: var(--accent); }

.hint {
  font-size: 0.72rem;
  color: var(--muted);
  margin-bottom: 16px;
  font-family: 'Space Mono', monospace;
  word-break: break-all;
}
code { color: var(--accent); }

.confirm-btn {
  width: 100%;
  background: var(--accent);
  color: #000;
  border: none;
  border-radius: 3px;
  font-family: 'Space Mono', monospace;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 12px;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.confirm-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.confirm-btn:not(:disabled):hover { background: var(--accent-bright); }

.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid rgba(0,0,0,0.3);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from { opacity: 0; transform: scale(0.95); }
.modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>