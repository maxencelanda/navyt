<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="video" class="overlay" @click.self="emit('close')">
        <div class="modal">
          <button class="close" @click="emit('close')">×</button>
          <div class="header">
            <img :src="video.thumbnail" :alt="video.title" class="thumb" />
            <div>
              <p class="video-title">{{ video.title }}</p>
              <p class="channel">{{ video.channel }}</p>
            </div>
          </div>

          <div class="fields">
            <label>
              <span>Title</span>
              <input v-model="form.title" type="text" :placeholder="video.title" />
            </label>
            <label>
              <span>Artist</span>
              <input v-model="form.artist" type="text" placeholder="Artist name" />
            </label>
            <label>
              <span>Album</span>
              <input v-model="form.album" type="text" placeholder="Album name" />
            </label>
          </div>

          <p class="hint">
            File will be saved as <code>{{ previewPath }}</code>
          </p>

          <button class="confirm-btn" :disabled="submitting" @click="submit">
            <span v-if="submitting" class="spinner" />
            <span v-else>Download as OPUS</span>
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

const form = reactive({ title: "", artist: "", album: "" });
const submitting = ref(false);

const sanitize = (s: string) => s.replace(/[^a-zA-Z0-9 .\-_()\[\]]/g, "_").trim();

const previewPath = computed(() => {
  const artist = sanitize(form.artist || "Unknown Artist");
  const album = sanitize(form.album || "Unknown Album");
  const title = sanitize(form.title || props.video?.title || "track");
  return `<MEDIA_DIR>/${artist}/${album}/${title}.opus`;
});

watch(() => props.video, (v) => {
  if (v) {
    form.title = "";
    form.artist = "";
    form.album = "";
    submitting.value = false;
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
  margin-bottom: 20px;
}
.thumb {
  width: 100px; height: 56px;
  object-fit: cover; border-radius: 3px; flex-shrink: 0;
}
.video-title {
  font-size: 0.88rem; font-weight: 500; color: var(--text);
  margin: 0 0 4px; font-family: 'DM Sans', sans-serif;
}
.channel { font-size: 0.78rem; color: var(--muted); margin: 0; }

.fields { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }

label {
  display: flex; flex-direction: column; gap: 5px;
}
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

.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from { opacity: 0; transform: scale(0.95); }
.modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>