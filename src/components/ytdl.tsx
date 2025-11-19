// actions.tsx or YouTubeDownloader.tsx

import React, { useState } from "react";

export default function YouTubeDownloader() {
  const [url, setUrl] = useState("");
  const [progress, setProgress] = useState<number | null>(null);
  const [status, setStatus] = useState<
    "idle" | "in_progress" | "complete" | "error"
  >("idle");

  const handleDownload = async () => {
    setStatus("in_progress");
    setProgress(0);

    const body = {
      url,
      quality: "720",
      format_: "mp4",
      audio_quality: "192",
      save_thumbnail: false,
      output_dir: "/Users/zai/Desktop/plex/Podcasts",
      filename_suffix: "",
    };

    await fetch("http://localhost:8000/yt/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    pollProgress(url);
  };

  const pollProgress = (url: string) => {
    const encoded = encodeURIComponent(url);
    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/yt/progress?url=${encoded}`
        );
        const data = await res.json();

        if (data.percent != null) {
          setProgress(data.percent);

          if (data.percent >= 100 || data.status === "finished") {
            clearInterval(interval);
            setStatus("complete");
          }
        }
      } catch (err) {
        console.error("Error polling progress:", err);
        clearInterval(interval);
        setStatus("error");
      }
    }, 2000);
  };

  return (
    <div>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter YouTube URL"
      />
      <button onClick={handleDownload}>Download</button>

      {status === "in_progress" && <p>Downloading: {progress?.toFixed(1)}%</p>}
      {status === "complete" && <p>✅ Done!</p>}
    </div>
  );
}
