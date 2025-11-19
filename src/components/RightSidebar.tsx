// components/RightSidebar.tsx
import * as React from "react";
import { useState, useEffect } from "react";
import { supabase } from "@/supabase/supabaseClient";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar";

import { NavMainWithThreads } from "@/components/nav-main-with-threads";
import { NavProjects } from "@/components/Sidebar/nav-projects";
import { NavUser } from "@/components/Sidebar/nav-user";
import { TeamSwitcher } from "@/components/Sidebar/team-switcher";

// Sample data (same as AppSidebar)
const data = {
  navMain: [
    {
      title: "Threads",
      url: "#",
      icon: undefined,
      isActive: true,
      items: [],
    },
    {
      title: "Playground",
      url: "#",
      icon: undefined,
      items: [
        { title: "History", url: "#" },
        { title: "Starred", url: "#" },
        { title: "Settings", url: "#" },
      ],
    },
    {
      title: "Models",
      url: "#",
      icon: undefined,
      items: [
        { title: "Genesis", url: "#" },
        { title: "Explorer", url: "#" },
        { title: "Quantum", url: "#" },
      ],
    },
  ],
  projects: [
    { name: "Design Engineering", url: "#", icon: undefined },
    { name: "Sales & Marketing", url: "#", icon: undefined },
    { name: "Travel", url: "#", icon: undefined },
  ],
};

export function RightSidebar({
  activePersona,
  onPersonaChange,
  currentThreadId,
  onThreadSelect,
  onSidebarClose,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  activePersona?: string;
  onPersonaChange?: (personaName: string) => void;
  currentThreadId?: string;
  onThreadSelect?: (threadId: string) => void;
  onSidebarClose?: () => void;
}) {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const getUser = async () => {
      const { data, error } = await supabase.auth.getUser();
      if (!error && data?.user) setUser(data.user);
    };
    getUser();
  }, []);

  const userData = {
    name: user?.user_metadata?.name || "User",
    email: user?.email || "user@example.com",
    avatar: user?.user_metadata?.avatar_url || "",
  };

  return (
    <Sidebar
      collapsible="icon"
      className="border-l-0 border-none right-0 left-auto" // push to right
      style={{
        borderLeft: "none",
        border: "none",
        right: 0,
        left: "auto",
      }}
      {...props}
    >
      <SidebarHeader>
        <TeamSwitcher
          activePersona={activePersona}
          onPersonaChange={onPersonaChange}
        />
      </SidebarHeader>

      <SidebarContent>
        <NavMainWithThreads
          items={data.navMain}
          currentThreadId={currentThreadId}
          onThreadSelect={onThreadSelect}
          onSidebarClose={onSidebarClose}
        />
        <NavProjects projects={data.projects} />
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={userData} />
      </SidebarFooter>
    </Sidebar>
  );
}
