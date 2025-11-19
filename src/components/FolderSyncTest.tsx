import React from "react";
import { useFolders } from "@/hooks/useFolders";

// Simple test component to verify folder synchronization
export function FolderSyncTest() {
  const { folders, threads, loading } = useFolders();

  if (loading) {
    return <div>Loading folders...</div>;
  }

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-semibold mb-2">Folder Sync Test</h3>
      <p className="text-sm text-gray-600 mb-2">
        Folders: {folders.length} | Threads: {threads.length}
      </p>
      <div className="space-y-1">
        {folders.map((folder) => (
          <div key={folder.id} className="text-xs">
            📁 {folder.name} ({folder.icon})
          </div>
        ))}
      </div>
    </div>
  );
}
