import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Plus,
  Home,
  Circle,
  Zap,
  Sparkles,
  MoreHorizontal,
  Edit3,
  Trash2,
  X,
  Menu,
  ChevronDown,
  ChevronRight,
  FolderPlus,
  Folder,
  MessageSquare,
  FolderOpen,
  MoreVertical,
  Star,
  Archive,
  Trash,
  Settings,
  Palette,
  Code,
  BookOpen,
  Briefcase,
  Heart,
  Lightbulb,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/supabase/supabaseClient";
import { isToday, isYesterday, isThisWeek, isThisMonth } from "date-fns";
import React from "react"; // Added missing import for React

type SidebarProps = {
  theme: "light" | "dark" | "system";
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
};

type Thread = {
  id: string;
  name: string;
  created_at: string;
  date_modified: string;
  folder_id?: string;
};

type Folder = {
  id: string;
  name: string;
  created_at: string;
  isExpanded: boolean;
  icon: string;
  color: string;
  description?: string;
};

// Custom type for pan info
type PanInfo = {
  point: { x: number; y: number };
  velocity: { x: number; y: number };
};

// Folder icons and colors
const FOLDER_ICONS = [
  { name: "Star", icon: Star, color: "text-yellow-500" },
  { name: "Archive", icon: Archive, color: "text-blue-500" },
  { name: "Code", icon: Code, color: "text-green-500" },
  { name: "Book", icon: BookOpen, color: "text-purple-500" },
  { name: "Briefcase", icon: Briefcase, color: "text-indigo-500" },
  { name: "Heart", icon: Heart, color: "text-pink-500" },
  { name: "Lightbulb", icon: Lightbulb, color: "text-orange-500" },
  { name: "Settings", icon: Settings, color: "text-gray-500" },
  { name: "Palette", icon: Palette, color: "text-cyan-500" },
];

const FOLDER_COLORS = [
  "bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950 dark:border-blue-800 dark:text-blue-300",
  "bg-green-50 border-green-200 text-green-700 dark:bg-green-950 dark:border-green-800 dark:text-green-300",
  "bg-purple-50 border-purple-200 text-purple-700 dark:bg-purple-950 dark:border-purple-800 dark:text-purple-300",
  "bg-pink-50 border-pink-200 text-pink-700 dark:bg-pink-950 dark:border-pink-800 dark:text-pink-300",
  "bg-orange-50 border-orange-200 text-orange-700 dark:bg-orange-950 dark:border-orange-800 dark:text-orange-300",
  "bg-cyan-50 border-cyan-200 text-cyan-700 dark:bg-cyan-950 dark:border-cyan-800 dark:text-cyan-300",
  "bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-950 dark:border-yellow-800 dark:text-yellow-300",
  "bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300",
];

function groupThreadsByDate(threads: Thread[]) {
  const groups: Record<string, Thread[]> = {
    Today: [],
    Yesterday: [],
    "This Week": [],
    "This Month": [],
    Older: [],
  };

  threads.forEach((thread) => {
    const date = new Date(thread.date_modified || thread.created_at);
    if (isToday(date)) groups["Today"].push(thread);
    else if (isYesterday(date)) groups["Yesterday"].push(thread);
    else if (isThisWeek(date)) groups["This Week"].push(thread);
    else if (isThisMonth(date)) groups["This Month"].push(thread);
    else groups["Older"].push(thread);
  });

  return groups;
}

export default function Sidebar({
  theme,
  sidebarOpen,
  setSidebarOpen,
}: SidebarProps) {
  const [user, setUser] = useState<any>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [folders, setFolders] = useState<Folder[]>([
    {
      id: "1",
      name: "Favorites",
      created_at: new Date().toISOString(),
      isExpanded: true,
      icon: "Star",
      color:
        "bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-950 dark:border-yellow-800 dark:text-yellow-300",
      description: "Your most important conversations",
    },
    {
      id: "2",
      name: "Work",
      created_at: new Date().toISOString(),
      isExpanded: false,
      icon: "Briefcase",
      color:
        "bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300",
      description: "Professional discussions and projects",
    },
    {
      id: "3",
      name: "Learning",
      created_at: new Date().toISOString(),
      isExpanded: true,
      icon: "BookOpen",
      color:
        "bg-purple-50 border-purple-200 text-purple-700 dark:bg-purple-950 dark:border-purple-800 dark:text-purple-300",
      description: "Educational content and tutorials",
    },
  ]);
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null);
  const [draftNames, setDraftNames] = useState<Record<string, string>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [dragStart, setDragStart] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [newFolderIcon, setNewFolderIcon] = useState("Star");
  const [newFolderColor, setNewFolderColor] = useState(FOLDER_COLORS[0]);

  const navigate = useNavigate();
  const sidebarRef = useRef<HTMLDivElement>(null);

  // Load user and threads
  useEffect(() => {
    const loadData = async () => {
      const { data: userData } = await supabase.auth.getUser();
      if (userData.user) {
        setUser(userData.user);

        // Load threads
        const { data: threadsData } = await supabase
          .from("chat_threads")
          .select("*")
          .eq("user_id", userData.user.id)
          .order("date_modified", { ascending: false });
        setThreads(threadsData || []);
      }
    };
    loadData();
  }, []);

  // iOS-style swipe gestures
  const handleDragStart = useCallback((event: any, info: PanInfo) => {
    setDragStart(info.point.x);
    setIsDragging(true);
  }, []);

  const handleDrag = useCallback(
    (event: any, info: PanInfo) => {
      if (!sidebarRef.current) return;
      const deltaX = info.point.x - dragStart;
      if (deltaX < 0) return;

      const maxDrag = 280;
      const progress = Math.min(deltaX / maxDrag, 1);
      sidebarRef.current.style.transform = `translateX(${
        -280 + 280 * progress
      }px)`;
    },
    [dragStart]
  );

  const handleDragEnd = useCallback(
    (event: any, info: PanInfo) => {
      setIsDragging(false);
      if (!sidebarRef.current) return;

      const deltaX = info.point.x - dragStart;
      const velocity = info.velocity.x;

      if (deltaX < -50 || velocity < -500) {
        setSidebarOpen(false);
      } else {
        sidebarRef.current.style.transform = "translateX(0px)";
      }
    },
    [dragStart, setSidebarOpen]
  );

  // Filter threads
  const filteredThreads = threads.filter((thread) =>
    thread.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const groupedThreads = groupThreadsByDate(filteredThreads);

  // Create new thread
  const createNewThread = async () => {
    const { data: userData } = await supabase.auth.getUser();
    if (!userData.user) return;

    const { data: newThread, error } = await supabase
      .from("chat_threads")
      .insert([
        {
          user_id: userData.user.id,
          name: "New Chat",
          model: "Groq-LLaMA3-70B",
        },
      ])
      .select()
      .single();

    if (!error && newThread) {
      setThreads((prev) => [newThread, ...prev]);
      navigate(`/chat/${newThread.id}`);
      setSidebarOpen(false);
    }
  };

  // Create new folder
  const createNewFolder = () => {
    if (!newFolderName.trim()) return;

    const newFolder: Folder = {
      id: Date.now().toString(),
      name: newFolderName.trim(),
      created_at: new Date().toISOString(),
      isExpanded: true,
      icon: newFolderIcon,
      color: newFolderColor,
      description: `A collection of ${newFolderName.toLowerCase()} conversations`,
    };

    setFolders((prev) => [newFolder, ...prev]);
    setNewFolderName("");
    setNewFolderIcon("Star");
    setNewFolderColor(FOLDER_COLORS[0]);
    setShowCreateFolder(false);
  };

  // Toggle folder expansion
  const toggleFolder = (folderId: string) => {
    setFolders((prev) =>
      prev.map((f) =>
        f.id === folderId ? { ...f, isExpanded: !f.isExpanded } : f
      )
    );
  };

  // Delete thread
  const deleteThread = async (threadId: string) => {
    const { error } = await supabase
      .from("chat_threads")
      .delete()
      .eq("id", threadId);

    if (!error) {
      setThreads((prev) => prev.filter((t) => t.id !== threadId));
    }
  };

  // Delete folder
  const deleteFolder = (folderId: string) => {
    setFolders((prev) => prev.filter((f) => f.id !== folderId));
    // Move threads in this folder to ungrouped
    setThreads((prev) =>
      prev.map((t) =>
        t.folder_id === folderId ? { ...t, folder_id: null } : t
      )
    );
  };

  // Save thread name
  const saveThreadName = async (threadId: string) => {
    const name = draftNames[threadId]?.trim();
    if (!name) {
      setEditingThreadId(null);
      return;
    }

    const { error } = await supabase
      .from("chat_threads")
      .update({ name, date_modified: new Date().toISOString() })
      .eq("id", threadId);

    if (!error) {
      setThreads((prev) =>
        prev.map((t) => (t.id === threadId ? { ...t, name } : t))
      );
    }
    setEditingThreadId(null);
  };

  // Save folder name
  const saveFolderName = (folderId: string) => {
    const name = draftNames[folderId]?.trim();
    if (!name) {
      setEditingFolderId(null);
      return;
    }

    setFolders((prev) =>
      prev.map((f) => (f.id === folderId ? { ...f, name } : f))
    );
    setEditingFolderId(null);
  };

  // Move thread to folder
  const moveThreadToFolder = (threadId: string, folderId: string | null) => {
    setThreads((prev) =>
      prev.map((t) => (t.id === threadId ? { ...t, folder_id: folderId } : t))
    );
  };

  // Handle thread click
  const handleThreadClick = (threadId: string) => {
    navigate(`/chat/${threadId}`);
    setSidebarOpen(false);
  };

  // Handle logout
  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.href = "/AuthBox";
  };

  const isDark = theme === "dark";

  const getFolderIcon = (iconName: string) => {
    const iconConfig = FOLDER_ICONS.find((icon) => icon.name === iconName);
    return iconConfig ? iconConfig.icon : Folder;
  };

  const getFolderIconColor = (iconName: string) => {
    const iconConfig = FOLDER_ICONS.find((icon) => icon.name === iconName);
    return iconConfig ? iconConfig.color : "text-gray-500";
  };

  return (
    <>
      {/* iOS-style backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.32, 0.72, 0, 1] }}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Main Sidebar - ChatGPT iOS style */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            ref={sidebarRef}
            drag="x"
            dragConstraints={{ left: -280, right: 0 }}
            dragElastic={0.1}
            onDragStart={handleDragStart}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{
              type: "spring",
              damping: 25,
              stiffness: 200,
              duration: 0.35,
              ease: [0.32, 0.72, 0, 1],
            }}
            className={`fixed left-0 top-0 h-full w-80 z-50 flex flex-col ${
              isDark ? "bg-black text-white" : "bg-white text-gray-900"
            } shadow-2xl`}
          >
            {/* Header - ChatGPT iOS style */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200/10 dark:border-gray-700/10">
              <h1 className="text-lg font-semibold">GlowGPT</h1>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Search - iOS style */}
            <div className="px-4 pb-3 pt-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search conversations"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-10 rounded-full border-0.5"
                />
              </div>
            </div>

            {/* Navigation - iOS style */}
            <div className="px-4 pb-3 space-y-0.5">
              {[
                { icon: Home, label: "Home", path: "/chat" },
                { icon: Circle, label: "Luma", path: "/luma" },
                { icon: Zap, label: "Superpowers", path: "/superbrowse" },
                { icon: Sparkles, label: "GPTs", path: "/gpts" },
              ].map(({ icon: Icon, label, path }) => (
                <Button
                  key={label}
                  onClick={() => {
                    navigate(path);
                    setSidebarOpen(false);
                  }}
                  variant="ghost"
                  className="w-full justify-start gap-3 h-9 text-sm font-medium"
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Button>
              ))}
            </div>

            {/* Folders Section */}
            <div className="px-4 pb-3">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Folders
                </h3>
                <Dialog
                  open={showCreateFolder}
                  onOpenChange={setShowCreateFolder}
                >
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 hover:bg-gray-100 dark:hover:bg-gray-800"
                    >
                      <FolderPlus className="w-3 h-3" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="w-[95vw] max-w-md mx-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-xl rounded-2xl">
                    <DialogHeader className="px-6 pt-6 pb-2">
                      <DialogTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                        Create New Folder
                      </DialogTitle>
                      <DialogDescription className="text-sm text-gray-600 dark:text-gray-400">
                        Organize your conversations with custom folders.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-6 py-4 px-6">
                      <div className="space-y-2">
                        <Label
                          htmlFor="folder-name"
                          className="text-sm font-medium text-gray-900 dark:text-white"
                        >
                          Folder Name
                        </Label>
                        <Input
                          id="folder-name"
                          value={newFolderName}
                          onChange={(e) => setNewFolderName(e.target.value)}
                          placeholder="Enter folder name"
                          className="h-10 rounded-lg border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                      </div>
                      <div className="space-y-3">
                        <Label className="text-sm font-medium text-gray-900 dark:text-white">
                          Choose Icon
                        </Label>
                        <div className="grid grid-cols-3 gap-3">
                          {FOLDER_ICONS.map(({ name, icon: Icon, color }) => (
                            <Button
                              key={name}
                              variant={
                                newFolderIcon === name ? "default" : "outline"
                              }
                              size="sm"
                              onClick={() => setNewFolderIcon(name)}
                              className={`h-12 justify-start gap-3 rounded-lg transition-all ${
                                newFolderIcon === name
                                  ? "bg-blue-500 hover:bg-blue-600 text-white"
                                  : "hover:bg-gray-50 dark:hover:bg-gray-800 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                              }`}
                            >
                              <Icon className={`w-4 h-4 ${color}`} />
                              <span className="text-xs font-medium">
                                {name}
                              </span>
                            </Button>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-3">
                        <Label className="text-sm font-medium text-gray-900 dark:text-white">
                          Color Theme
                        </Label>
                        <div className="grid grid-cols-2 gap-3">
                          {FOLDER_COLORS.map((color, index) => (
                            <Button
                              key={index}
                              variant={
                                newFolderColor === color ? "default" : "outline"
                              }
                              size="sm"
                              onClick={() => setNewFolderColor(color)}
                              className={`h-10 rounded-lg border-2 transition-all ${
                                newFolderColor === color
                                  ? "ring-2 ring-blue-500 ring-offset-2"
                                  : ""
                              } ${color}`}
                            >
                              <span className="text-xs font-medium">
                                {color.includes("blue") && "Blue"}
                                {color.includes("green") && "Green"}
                                {color.includes("purple") && "Purple"}
                                {color.includes("pink") && "Pink"}
                                {color.includes("orange") && "Orange"}
                                {color.includes("cyan") && "Cyan"}
                                {color.includes("yellow") && "Yellow"}
                                {color.includes("indigo") && "Indigo"}
                              </span>
                            </Button>
                          ))}
                        </div>
                      </div>
                    </div>
                    <DialogFooter className="gap-2 px-6 pb-6">
                      <Button
                        variant="outline"
                        onClick={() => setShowCreateFolder(false)}
                        className="rounded-lg border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={createNewFolder}
                        disabled={!newFolderName.trim()}
                        className="rounded-lg bg-blue-500 hover:bg-blue-600"
                      >
                        Create Folder
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="space-y-2">
                {folders.map((folder) => {
                  const IconComponent = getFolderIcon(folder.icon);
                  const iconColor = getFolderIconColor(folder.icon);
                  const threadsInFolder = threads.filter(
                    (thread) => thread.folder_id === folder.id
                  );

                  return (
                    <Card
                      key={folder.id}
                      className={`${folder.color} border transition-all duration-200 hover:shadow-md`}
                    >
                      <CardContent className="p-0">
                        <div className="flex items-center p-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleFolder(folder.id)}
                            className="h-6 w-6 p-0 mr-2"
                          >
                            {folder.isExpanded ? (
                              <ChevronDown className="w-3 h-3" />
                            ) : (
                              <ChevronRight className="w-3 h-3" />
                            )}
                          </Button>
                          <IconComponent
                            className={`w-4 h-4 mr-2 ${iconColor}`}
                          />
                          {editingFolderId === folder.id ? (
                            <Input
                              type="text"
                              value={draftNames[folder.id] || folder.name}
                              onChange={(e) =>
                                setDraftNames((prev) => ({
                                  ...prev,
                                  [folder.id]: e.target.value,
                                }))
                              }
                              onBlur={() => saveFolderName(folder.id)}
                              onKeyDown={(e) => {
                                if (e.key === "Enter")
                                  saveFolderName(folder.id);
                                if (e.key === "Escape")
                                  setEditingFolderId(null);
                              }}
                              className="flex-1 h-6 text-sm font-medium bg-transparent border-none p-0 focus-visible:ring-0"
                              autoFocus
                            />
                          ) : (
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold truncate">
                                  {folder.name}
                                </span>
                                <Badge
                                  variant="secondary"
                                  className="text-xs h-4 px-1.5"
                                >
                                  {threadsInFolder.length}
                                </Badge>
                              </div>
                              <p className="text-xs font-medium opacity-80 truncate">
                                {folder.description}
                              </p>
                            </div>
                          )}
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <MoreVertical className="w-3 h-3" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>
                                Folder Actions
                              </DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => {
                                  setEditingFolderId(folder.id);
                                  setDraftNames((prev) => ({
                                    ...prev,
                                    [folder.id]: folder.name,
                                  }));
                                }}
                              >
                                <Edit3 className="w-3 h-3 mr-2" />
                                Rename
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => {
                                  if (confirm("Delete this folder?")) {
                                    deleteFolder(folder.id);
                                  }
                                }}
                                className="text-red-600 dark:text-red-400"
                              >
                                <Trash2 className="w-3 h-3 mr-2" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>

                        {folder.isExpanded && threadsInFolder.length > 0 && (
                          <div className="px-3 pb-3 space-y-1">
                            {threadsInFolder.map((thread) => (
                              <div
                                key={thread.id}
                                className="group/thread flex items-center rounded-md hover:bg-white/50 dark:hover:bg-black/20 transition-colors p-1"
                              >
                                <MessageSquare className="w-3 h-3 mr-2 opacity-60" />
                                <button
                                  onClick={() => handleThreadClick(thread.id)}
                                  className="flex-1 text-left text-xs truncate"
                                >
                                  {thread.name || "Untitled Chat"}
                                </button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    moveThreadToFolder(thread.id, null)
                                  }
                                  className="h-5 w-5 p-0 opacity-0 group-hover/thread:opacity-100 transition-opacity"
                                >
                                  <X className="w-3 h-3" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* Threads List - iOS style */}
            <div className="flex-1 overflow-y-auto px-4">
              {Object.entries(groupedThreads).map(
                ([label, threadGroup]) =>
                  threadGroup.length > 0 && (
                    <div key={label} className="mb-4">
                      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        {label}
                      </h3>
                      <div className="space-y-1">
                        {threadGroup.map((thread) => (
                          <div
                            key={thread.id}
                            className="group relative flex items-center rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors p-2"
                          >
                            <MessageSquare className="w-4 h-4 mr-2 text-gray-400" />
                            {editingThreadId === thread.id ? (
                              <Input
                                type="text"
                                value={draftNames[thread.id] || thread.name}
                                onChange={(e) =>
                                  setDraftNames((prev) => ({
                                    ...prev,
                                    [thread.id]: e.target.value,
                                  }))
                                }
                                onBlur={() => saveThreadName(thread.id)}
                                onKeyDown={(e) => {
                                  if (e.key === "Enter")
                                    saveThreadName(thread.id);
                                  if (e.key === "Escape")
                                    setEditingThreadId(null);
                                }}
                                className="flex-1 h-6 text-sm bg-transparent border-none p-0 focus-visible:ring-0"
                                autoFocus
                              />
                            ) : (
                              <>
                                <button
                                  onClick={() => handleThreadClick(thread.id)}
                                  className="flex-1 text-left text-sm truncate"
                                >
                                  {thread.name || "Untitled Chat"}
                                </button>

                                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                                  <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-6 w-6 p-0"
                                      >
                                        <MoreVertical className="w-3 h-3" />
                                      </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                      <DropdownMenuLabel>
                                        Move to folder
                                      </DropdownMenuLabel>
                                      <DropdownMenuSeparator />
                                      <DropdownMenuItem
                                        onClick={() =>
                                          moveThreadToFolder(thread.id, null)
                                        }
                                      >
                                        <X className="w-3 h-3 mr-2" />
                                        Remove from folder
                                      </DropdownMenuItem>
                                      {folders.map((folder) => (
                                        <DropdownMenuItem
                                          key={folder.id}
                                          onClick={() =>
                                            moveThreadToFolder(
                                              thread.id,
                                              folder.id
                                            )
                                          }
                                        >
                                          {React.createElement(
                                            getFolderIcon(folder.icon),
                                            {
                                              className: `w-3 h-3 mr-2 ${getFolderIconColor(
                                                folder.icon
                                              )}`,
                                            }
                                          )}
                                          {folder.name}
                                        </DropdownMenuItem>
                                      ))}
                                      <DropdownMenuSeparator />
                                      <DropdownMenuItem
                                        onClick={() => {
                                          setEditingThreadId(thread.id);
                                          setDraftNames((prev) => ({
                                            ...prev,
                                            [thread.id]: thread.name,
                                          }));
                                        }}
                                      >
                                        <Edit3 className="w-3 h-3 mr-2" />
                                        Rename
                                      </DropdownMenuItem>
                                      <DropdownMenuItem
                                        onClick={() => {
                                          if (confirm("Delete this chat?")) {
                                            deleteThread(thread.id);
                                          }
                                        }}
                                        className="text-red-600 dark:text-red-400"
                                      >
                                        <Trash2 className="w-3 h-3 mr-2" />
                                        Delete
                                      </DropdownMenuItem>
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )
              )}
            </div>

            {/* User Profile - iOS style */}
            <div className="p-4 border-t border-gray-200/10 dark:border-gray-700/10">
              <div className="flex items-center gap-3">
                <Avatar className="w-8 h-8">
                  <AvatarImage src={user?.user_metadata?.avatar_url} />
                  <AvatarFallback className="bg-gray-200 dark:bg-gray-700 text-xs font-semibold">
                    {user?.user_metadata?.name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {user?.user_metadata?.name || "User"}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.email}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="h-8 w-8 p-0"
                >
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
