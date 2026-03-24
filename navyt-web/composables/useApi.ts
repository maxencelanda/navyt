export const useApi = () => {
  const config = useRuntimeConfig();
  const base = config.public.apiBase;

  const search = async (query: string, maxResults = 20) => {
    const data = await $fetch<{ results: any[] }>(
      `${base}/api/search?q=${encodeURIComponent(query)}&max_results=${maxResults}`
    );
    return data.results;
  };

  const getVideoInfo = async (videoId: string) => {
    return $fetch<any>(`${base}/api/search/${videoId}`);
  };

  const startDownload = async (payload: {
    video_id: string;
    title?: string;
    artist?: string;
    album?: string;
  }) => {
    return $fetch<any>(`${base}/api/downloads`, {
      method: "POST",
      body: payload,
    });
  };

  const listDownloads = async () => {
    const data = await $fetch<{ jobs: any[] }>(`${base}/api/downloads`);
    return data.jobs;
  };

  const getJob = async (jobId: string) => {
    return $fetch<any>(`${base}/api/downloads/${jobId}`);
  };

  const deleteJob = async (jobId: string) => {
    return $fetch<any>(`${base}/api/downloads/${jobId}`, { method: "DELETE" });
  };

  return { search, getVideoInfo, startDownload, listDownloads, getJob, deleteJob };
};