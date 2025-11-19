import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  Home,
  ArrowLeft,
  ArrowRight,
  Grid,
  List,
  Folder,
  File,
  Star,
  Clock,
  Download,
  Image,
  Music,
  Video,
  Code,
  Archive,
  FileText,
  Settings,
  ChevronDown,
  ChevronRight,
  MoreHorizontal,
} from "lucide-react";

interface FileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
  mode?: "directory" | "file";
  title?: string;
  initialPath?: string | null;
}

interface FileItem {
  name: string;
  path: string;
  type: "file" | "directory";
  size?: number;
  modified?: number;
  extension?: string;
}

interface SidebarItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  type: "location" | "favorite" | "recent";
}

const ViewModes = {
  GRID: "grid",
  LIST: "list",
} as const;

const getFileIcon = (file: FileItem) => {
  if (file.type === "directory")
    return <Folder className="w-5 h-5 text-blue-500" />;

  const ext = file.extension?.toLowerCase();
  if (["jpg", "png", "gif", "svg", "webp"].includes(ext || ""))
    return <Image className="w-5 h-5 text-green-500" />;
  if (["mp3", "wav", "flac", "m4a"].includes(ext || ""))
    return <Music className="w-5 h-5 text-purple-500" />;
  if (["mp4", "avi", "mkv", "mov"].includes(ext || ""))
    return <Video className="w-5 h-5 text-red-500" />;
  if (["js", "ts", "py", "java", "cpp"].includes(ext || ""))
    return <Code className="w-5 h-5 text-orange-500" />;
  if (["zip", "rar", "7z", "tar"].includes(ext || ""))
    return <Archive className="w-5 h-5 text-yellow-600" />;
  if (["txt", "md", "doc", "pdf"].includes(ext || ""))
    return <FileText className="w-5 h-5 text-gray-500" />;

  return <File className="w-5 h-5 text-gray-400" />;
};

const formatFileSize = (bytes: number) => {
  if (!bytes) return "";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleDateString();
};

export const FileModal: React.FC<FileModalProps> = ({
  isOpen,
  onClose,
  onSelect,
  mode = "directory",
  title = "Select Directory",
  initialPath = null,
}) => {
  const [currentPath, setCurrentPath] = useState(initialPath || "/");
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<FileItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedPath, setSelectedPath] = useState("");
  const [viewMode, setViewMode] = useState<keyof typeof ViewModes>("GRID");
  const [history, setHistory] = useState<string[]>(["/"]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [favorites, setFavorites] = useState<string[]>([
    "/",
    "/Users",
    "/Applications",
  ]);
  const [recents, setRecents] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"name" | "size" | "modified">("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const API_BASE = "https://100.83.147.76:8003";
  const fileListRef = useRef<HTMLDivElement>(null);

  const sidebarItems: SidebarItem[] = [
    {
      name: "Home",
      path: "/",
      icon: <Home className="w-4 h-4" />,
      type: "location",
    },
    {
      name: "Desktop",
      path: "/Users/zai/Desktop",
      icon: <Folder className="w-4 h-4" />,
      type: "location",
    },
    {
      name: "Plex",
      path: "/Users/zai/Desktop/plex",
      icon: <FileText className="w-4 h-4" />,
      type: "location",
    },
    {
      name: "Downloads",
      path: "/Users/zai/Downloads",
      icon: <Download className="w-4 h-4" />,
      type: "location",
    },
    ...favorites.map((path) => ({
      name: path.split("/").pop() || "Root",
      path,
      icon: <Star className="w-4 h-4 text-yellow-500" />,
      type: "favorite" as const,
    })),
    ...recents.slice(0, 5).map((path) => ({
      name: path.split("/").pop() || "Root",
      path,
      icon: <Clock className="w-4 h-4 text-gray-500" />,
      type: "recent" as const,
    })),
  ];

  const loadDirectory = useCallback(
    async (path: string) => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE}/api/superpowers/file_ops/execute`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              intent: "list_files",
              kwargs: { directory: path, show_hidden: false },
            }),
          }
        );

        const data = await response.json();
        if (data.result?.success) {
          const processedFiles = data.result.files.map((file: any) => ({
            ...file,
            extension:
              file.type === "file" ? file.name.split(".").pop() : undefined,
          }));

          const sorted = [...processedFiles].sort((a, b) => {
            if (a.type === "directory" && b.type === "file") return -1;
            if (a.type === "file" && b.type === "directory") return 1;

            let comparison = 0;
            switch (sortBy) {
              case "size":
                comparison = (a.size || 0) - (b.size || 0);
                break;
              case "modified":
                comparison = (a.modified || 0) - (b.modified || 0);
                break;
              default:
                comparison = a.name.localeCompare(b.name);
            }
            return sortOrder === "asc" ? comparison : -comparison;
          });

          setFiles(sorted);
        }
      } catch (err) {
        console.error("Failed to load directory:", err);
      } finally {
        setLoading(false);
      }
    },
    [sortBy, sortOrder]
  );

  const [allFiles, setAllFiles] = useState<FileItem[]>([]);

  const collectAllFiles = useCallback(
    async (directory = "/", collected: FileItem[] = []) => {
      try {
        const response = await fetch(
          `${API_BASE}/api/superpowers/file_ops/execute`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              intent: "list_files",
              kwargs: { directory, show_hidden: false },
            }),
          }
        );

        const data = await response.json();
        if (data.result?.success) {
          for (const file of data.result.files) {
            collected.push(file);
            if (file.type === "directory") {
              await collectAllFiles(file.path, collected);
            }
          }
        }
      } catch (err) {
        console.error("Failed to collect files from", directory, err);
      }
      return collected;
    },
    []
  );

  const performGlobalSearch = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        setSearchResults([]);
        setIsSearching(false);
        return;
      }

      setIsSearching(true);
      try {
        // Use cached files if available, otherwise collect them
        let filesToSearch = allFiles;
        if (allFiles.length === 0) {
          filesToSearch = await collectAllFiles();
          setAllFiles(filesToSearch);
        }

        // Filter files by name containing search term
        const results = filesToSearch.filter((file) =>
          file.name.toLowerCase().includes(query.toLowerCase())
        );

        setSearchResults(results);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setIsSearching(false);
      }
    },
    [allFiles, collectAllFiles]
  );

  const navigateTo = useCallback(
    (path: string) => {
      setCurrentPath(path);
      setSelectedPath(path);

      // Update history
      const newHistory = history.slice(0, historyIndex + 1);
      if (newHistory[newHistory.length - 1] !== path) {
        newHistory.push(path);
        setHistory(newHistory);
        setHistoryIndex(newHistory.length - 1);
      }

      // Update recents
      setRecents((prev) =>
        [path, ...prev.filter((p) => p !== path)].slice(0, 10)
      );
    },
    [history, historyIndex]
  );

  const navigateBack = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setCurrentPath(history[newIndex]);
      setSelectedPath(history[newIndex]);
    }
  };

  const navigateForward = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setCurrentPath(history[newIndex]);
      setSelectedPath(history[newIndex]);
    }
  };

  const navigateUp = () => {
    const parent = currentPath.split("/").slice(0, -1).join("/") || "/";
    navigateTo(parent);
  };

  const toggleFavorite = (path: string) => {
    setFavorites((prev) =>
      prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
    );
  };

  const pathSegments = currentPath.split("/").filter(Boolean);
  const filteredFiles = searchTerm
    ? searchResults.filter((file) =>
        mode === "directory" ? file.type === "directory" : true
      )
    : files.filter(
        (file) =>
          file.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
          (mode === "directory" ? file.type === "directory" : true)
      );

  useEffect(() => {
    if (isOpen) {
      // If initialPath is provided and different from current path, navigate to it
      if (initialPath && initialPath !== currentPath) {
        navigateTo(initialPath);
      } else if (!initialPath || initialPath === currentPath) {
        loadDirectory(currentPath);
      }
    }
  }, [isOpen, initialPath]); // Only depend on isOpen and initialPath to avoid loops

  const GridView = ({ items }: { items: FileItem[] }) => (
    <div className="grid grid-cols-4 gap-4 p-4">
      {items.map((file) => (
        <div
          key={file.path}
          className={`flex flex-col items-center p-3 rounded-xl cursor-pointer transition-all hover:bg-gray-50 ${
            selectedPath === file.path
              ? "bg-blue-50 border-2 border-blue-300"
              : "border-2 border-transparent"
          }`}
          onClick={() => setSelectedPath(file.path)}
          onDoubleClick={() =>
            file.type === "directory" && navigateTo(file.path)
          }
        >
          <div className="mb-2">{getFileIcon(file)}</div>
          <div className="text-xs text-center text-gray-700 break-words max-w-full">
            {file.name}
          </div>
          {file.size && (
            <div className="text-xs text-gray-400 mt-1">
              {formatFileSize(file.size)}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const ListView = ({ items }: { items: FileItem[] }) => (
    <div className="divide-y divide-gray-100">
      <div className="grid grid-cols-12 gap-4 p-3 text-xs font-medium text-gray-500 bg-gray-50">
        <div
          className="col-span-6 flex items-center cursor-pointer hover:text-gray-700"
          onClick={() => setSortBy("name")}
        >
          Name {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
        </div>
        <div
          className="col-span-2 cursor-pointer hover:text-gray-700"
          onClick={() => setSortBy("size")}
        >
          Size {sortBy === "size" && (sortOrder === "asc" ? "↑" : "↓")}
        </div>
        <div
          className="col-span-4 cursor-pointer hover:text-gray-700"
          onClick={() => setSortBy("modified")}
        >
          Modified {sortBy === "modified" && (sortOrder === "asc" ? "↑" : "↓")}
        </div>
      </div>
      {items.map((file) => (
        <div
          key={file.path}
          className={`grid grid-cols-12 gap-4 p-3 cursor-pointer transition-colors hover:bg-gray-50 ${
            selectedPath === file.path
              ? "bg-blue-50 border-l-4 border-blue-500"
              : ""
          }`}
          onClick={() => setSelectedPath(file.path)}
          onDoubleClick={() =>
            file.type === "directory" && navigateTo(file.path)
          }
        >
          <div className="col-span-6 flex items-center space-x-3">
            {getFileIcon(file)}
            <span className="text-sm text-gray-700 truncate">{file.name}</span>
          </div>
          <div className="col-span-2 text-sm text-gray-500">
            {file.size ? formatFileSize(file.size) : "—"}
          </div>
          <div className="col-span-4 text-sm text-gray-500">
            {file.modified ? formatDate(file.modified) : "—"}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl h-[80vh] flex flex-col p-0 bg-white border border-gray-200 shadow-2xl rounded-2xl">
        {/* Header */}
        <DialogHeader className="p-4 pb-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-lg font-semibold text-gray-900">
              {title}
            </DialogTitle>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  setViewMode(viewMode === "GRID" ? "LIST" : "GRID")
                }
              >
                {viewMode === "GRID" ? (
                  <List className="w-4 h-4" />
                ) : (
                  <Grid className="w-4 h-4" />
                )}
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Toolbar */}
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={navigateBack}
                disabled={historyIndex === 0}
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={navigateForward}
                disabled={historyIndex === history.length - 1}
              >
                <ArrowRight className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={navigateUp}
                disabled={currentPath === "/"}
              >
                ↑
              </Button>
            </div>

            <div className="flex items-center space-x-1 text-sm bg-white rounded-lg px-3 py-1 border">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateTo("/")}
                className="h-auto p-1 text-xs"
              >
                ~
              </Button>
              {pathSegments.map((segment, index) => (
                <React.Fragment key={index}>
                  <ChevronRight className="w-3 h-3 text-gray-400" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      navigateTo(
                        "/" + pathSegments.slice(0, index + 1).join("/")
                      )
                    }
                    className="h-auto p-1 text-xs hover:bg-blue-50 hover:text-blue-600"
                  >
                    {segment}
                  </Button>
                </React.Fragment>
              ))}
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleFavorite(currentPath)}
              className={
                favorites.includes(currentPath) ? "text-yellow-500" : ""
              }
            >
              <Star className="w-4 h-4" />
            </Button>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search all files..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                performGlobalSearch(e.target.value);
              }}
              className="pl-10 bg-white border-gray-200 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-48 border-r border-gray-200 bg-gray-50 overflow-y-auto">
            <div className="p-3">
              {["location", "favorite", "recent"].map((section) => (
                <div key={section} className="mb-4">
                  <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                    {section === "location"
                      ? "Places"
                      : section === "favorite"
                      ? "Favorites"
                      : "Recent"}
                  </div>
                  {sidebarItems
                    .filter((item) => item.type === section)
                    .map((item) => (
                      <button
                        key={item.path}
                        onClick={() => navigateTo(item.path)}
                        className={`w-full flex items-center space-x-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                          currentPath === item.path
                            ? "bg-blue-100 text-blue-700"
                            : "text-gray-700 hover:bg-gray-100"
                        }`}
                      >
                        {item.icon}
                        <span className="truncate">{item.name}</span>
                      </button>
                    ))}
                </div>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div ref={fileListRef} className="flex-1 overflow-y-auto bg-white">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="flex flex-col items-center space-y-3">
                    <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent"></div>
                    <div className="text-gray-500 text-sm">Loading...</div>
                  </div>
                </div>
              ) : filteredFiles.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Folder className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <div className="text-gray-500">
                      {searchTerm ? "No matching files" : "Empty directory"}
                    </div>
                  </div>
                </div>
              ) : viewMode === "GRID" ? (
                <GridView items={filteredFiles} />
              ) : (
                <ListView items={filteredFiles} />
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-600 flex items-center space-x-2">
              {isSearching && (
                <div className="animate-spin rounded-full h-3 w-3 border border-blue-500 border-t-transparent"></div>
              )}
              <span>{filteredFiles.length} items</span>
              {searchTerm && (
                <span className="text-xs text-blue-600">Search Results</span>
              )}
            </div>
            <div className="text-xs font-mono text-gray-500">
              {selectedPath || "No selection"}
            </div>
          </div>
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                if (selectedPath) {
                  onSelect(selectedPath);
                  onClose();
                }
              }}
              disabled={!selectedPath}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Select {mode === "directory" ? "Directory" : "File"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
