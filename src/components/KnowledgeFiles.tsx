"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  Upload,
  Search,
  Plus,
  FolderPlus,
  FileText,
  Image,
  Video,
  Music,
  Archive,
  Code,
} from "lucide-react";
import { Files, Folder, File } from "@/components/animate-ui/components/files";

interface KnowledgeFilesProps {
  isOpen: boolean;
  onClose: () => void;
}

// Mock file data structure
interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  fileType?:
    | "document"
    | "image"
    | "video"
    | "audio"
    | "archive"
    | "code"
    | "other";
  size?: string;
  modified: Date;
  children?: FileItem[];
}

const mockFiles: FileItem[] = [
  {
    id: "1",
    name: "Research Papers",
    type: "folder",
    modified: new Date("2024-01-15"),
    children: [
      {
        id: "1-1",
        name: "AI Ethics Research.pdf",
        type: "file",
        fileType: "document",
        size: "2.4 MB",
        modified: new Date("2024-01-10"),
      },
      {
        id: "1-2",
        name: "Machine Learning Notes.md",
        type: "file",
        fileType: "code",
        size: "156 KB",
        modified: new Date("2024-01-12"),
      },
    ],
  },
  {
    id: "2",
    name: "Personal Notes",
    type: "folder",
    modified: new Date("2024-01-14"),
    children: [
      {
        id: "2-1",
        name: "Daily Journal.txt",
        type: "file",
        fileType: "document",
        size: "45 KB",
        modified: new Date("2024-01-14"),
      },
      {
        id: "2-2",
        name: "Goals 2024.md",
        type: "file",
        fileType: "document",
        size: "23 KB",
        modified: new Date("2024-01-01"),
      },
    ],
  },
  {
    id: "3",
    name: "Project Assets",
    type: "folder",
    modified: new Date("2024-01-13"),
    children: [
      {
        id: "3-1",
        name: "logo.png",
        type: "file",
        fileType: "image",
        size: "1.2 MB",
        modified: new Date("2024-01-13"),
      },
      {
        id: "3-2",
        name: "presentation.mp4",
        type: "file",
        fileType: "video",
        size: "15.7 MB",
        modified: new Date("2024-01-12"),
      },
    ],
  },
  {
    id: "4",
    name: "Quick Reference.pdf",
    type: "file",
    fileType: "document",
    size: "890 KB",
    modified: new Date("2024-01-08"),
  },
  {
    id: "5",
    name: "Code Snippets.js",
    type: "file",
    fileType: "code",
    size: "67 KB",
    modified: new Date("2024-01-11"),
  },
];

const getFileIcon = (fileType?: string) => {
  switch (fileType) {
    case "document":
      return <FileText className="w-4 h-4 text-blue-500" />;
    case "image":
      return <Image className="w-4 h-4 text-green-500" />;
    case "video":
      return <Video className="w-4 h-4 text-purple-500" />;
    case "audio":
      return <Music className="w-4 h-4 text-pink-500" />;
    case "archive":
      return <Archive className="w-4 h-4 text-orange-500" />;
    case "code":
      return <Code className="w-4 h-4 text-indigo-500" />;
    default:
      return <FileText className="w-4 h-4 text-gray-500" />;
  }
};

const formatDate = (date: Date) => {
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return date.toLocaleDateString();
};

const renderFileTree = (items: FileItem[]) => {
  return items.map((item) => {
    if (item.type === "folder") {
      return (
        <Folder key={item.id} name={item.name}>
          {item.children && renderFileTree(item.children)}
        </Folder>
      );
    } else {
      return (
        <File
          key={item.id}
          name={item.name}
          sideComponent={
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span>{item.size}</span>
              <span>{formatDate(item.modified)}</span>
            </div>
          }
        />
      );
    }
  });
};

export default function KnowledgeFiles({
  isOpen,
  onClose,
}: KnowledgeFilesProps) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedFiles, setSelectedFiles] = React.useState<string[]>([]);
  const [viewMode, setViewMode] = React.useState<"list" | "grid">("list");

  const filteredFiles = React.useMemo(() => {
    if (!searchQuery) return mockFiles;

    const filterRecursive = (items: FileItem[]): FileItem[] => {
      return items
        .filter((item) => {
          const matchesSearch = item.name
            .toLowerCase()
            .includes(searchQuery.toLowerCase());
          if (item.type === "folder" && item.children) {
            const filteredChildren = filterRecursive(item.children);
            return matchesSearch || filteredChildren.length > 0;
          }
          return matchesSearch;
        })
        .map((item) => {
          if (item.type === "folder" && item.children) {
            return { ...item, children: filterRecursive(item.children) };
          }
          return item;
        });
    };

    return filterRecursive(mockFiles);
  }, [searchQuery]);

  const handleFileSelect = (fileId: string) => {
    setSelectedFiles((prev) =>
      prev.includes(fileId)
        ? prev.filter((id) => id !== fileId)
        : [...prev, fileId]
    );
  };

  const handleUpload = () => {
    // TODO: Implement file upload functionality
    console.log("Upload file");
  };

  const handleNewFolder = () => {
    // TODO: Implement new folder creation
    console.log("Create new folder");
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-full max-w-4xl max-h-[80vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Knowledge Files
                </h2>
                <p className="text-sm text-gray-500">
                  Manage your documents and research
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Toolbar */}
          <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-gray-50/50">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
                />
              </div>

              <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === "list"
                      ? "bg-blue-100 text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === "grid"
                      ? "bg-blue-100 text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleNewFolder}
                className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <FolderPlus className="w-4 h-4" />
                New Folder
              </button>
              <button
                onClick={handleUpload}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700 transition-colors"
              >
                <Upload className="w-4 h-4" />
                Upload Files
              </button>
            </div>
          </div>

          {/* File Browser */}
          <div className="flex-1 overflow-hidden">
            <div className="h-[500px] overflow-auto">
              <Files className="border-0 bg-transparent">
                {filteredFiles.length > 0 ? (
                  renderFileTree(filteredFiles)
                ) : (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                    <FileText className="w-16 h-16 mb-4 opacity-50" />
                    <p className="text-lg font-medium mb-2">No files found</p>
                    <p className="text-sm text-gray-400">
                      {searchQuery
                        ? "Try adjusting your search terms"
                        : "Upload your first file to get started"}
                    </p>
                  </div>
                )}
              </Files>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t border-gray-100 bg-gray-50/50">
            <div className="text-sm text-gray-500">
              {selectedFiles.length > 0 ? (
                <span>
                  {selectedFiles.length} file
                  {selectedFiles.length !== 1 ? "s" : ""} selected
                </span>
              ) : (
                <span>Ready to organize your knowledge</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-xl transition-colors"
              >
                Cancel
              </button>
              {selectedFiles.length > 0 && (
                <button className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
                  Open Selected
                </button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
