import * as React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import { Heart, Sparkles, Brain, Users, BookOpen } from "lucide-react";

const navigationItems = [
  {
    title: "Foundation",
    href: "/the-glow-foundation",
    description: "The philosophy and mission behind The Glow Project",
    icon: Heart,
    items: [
      {
        title: "Our Mission",
        href: "/the-glow-foundation",
        description: "Healing from chaos to clarity",
      },
      {
        title: "The Glow Process",
        href: "/glow-process",
        description: "Your personalized framework",
      },
      {
        title: "Philosophy",
        href: "/the-glow-foundation#philosophy",
        description: "Understanding Chaos vs The Glow",
      },
    ],
  },
  {
    title: "Glow Process",
    href: "/glow-process",
    description: "A personalized healing framework",
    icon: Sparkles,
    items: [
      {
        title: "How It Works",
        href: "/glow-process",
        description: "7 phases of transformation",
      },
      {
        title: "Body Release",
        href: "/glow-process#body-release",
        description: "Ground into safety",
      },
      {
        title: "Create Your Process",
        href: "/glowgpt",
        description: "Build your custom journey",
      },
    ],
  },
  {
    title: "GlowGPT",
    href: "/glowgpt",
    description: "Your AI guide through The Glow Process",
    icon: Brain,
    items: [
      {
        title: "Download Desktop",
        href: "/glowgpt",
        description: "macOS & Windows apps",
      },
      {
        title: "Inner Intelligence",
        href: "/glowgpt#features",
        description: "Emotional healing & awareness",
      },
      {
        title: "Outer Intelligence",
        href: "/glowgpt#features",
        description: "Task automation & memory",
      },
    ],
  },
  {
    title: "ARSA Foundation",
    href: "/arsafoundation",
    description: "Support for those with ARSA",
    icon: Users,
    items: [
      {
        title: "Join Community",
        href: "/arsafoundation",
        description: "Connect with others",
      },
      {
        title: "Find Doctors",
        href: "/arsafoundation#doctors",
        description: "Specialist directory",
      },
      {
        title: "Resources",
        href: "/arsafoundation#resources",
        description: "Research & support",
      },
    ],
  },
  {
    title: "About",
    href: "/about",
    description: "Learn more about The Glow Project",
    icon: BookOpen,
    items: [
      {
        title: "Our Story",
        href: "/about",
        description: "The journey begins",
      },
      {
        title: "Contact",
        href: "/the-glow-foundation#contact",
        description: "Get in touch",
      },
    ],
  },
];

const ListItem = React.forwardRef<
  React.ElementRef<"a">,
  React.ComponentPropsWithoutRef<"a"> & { title: string; description: string }
>(({ className, title, description, href, ...props }, ref) => {
  const navigate = useNavigate();
  
  return (
    <li>
      <NavigationMenuLink asChild>
        <a
          ref={ref}
          href={href}
          onClick={(e) => {
            e.preventDefault();
            if (href) navigate(href);
          }}
          className={cn(
            "block select-none space-y-1 rounded-xl p-3 leading-none no-underline outline-none transition-colors hover:bg-white/5 focus:bg-white/5 group",
            className
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none text-white group-hover:text-[#e1e65c] transition-colors">
            {title}
          </div>
          <p className="line-clamp-2 text-xs leading-snug text-zinc-400">
            {description}
          </p>
        </a>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = "ListItem";

export default function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <NavigationMenu className="hidden md:flex ml-2">
      <NavigationMenuList className="gap-1">
        {navigationItems.map((navItem) => {
          const isActive = location.pathname === navItem.href;
          const Icon = navItem.icon;

          return (
            <NavigationMenuItem key={navItem.href}>
              <NavigationMenuTrigger
                className={cn(
                  "rounded-full px-4 py-2 text-sm font-medium transition-all duration-300 bg-transparent border-none h-auto",
                  isActive
                    ? "text-white bg-black/60 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]"
                    : "text-zinc-300 hover:text-white hover:bg-white/5 data-[state=open]:bg-white/5 data-[state=open]:text-white"
                )}
              >
                {navItem.title}
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <div className="w-[400px] p-4">
                  {/* Header */}
                  <div className="mb-3 flex items-start gap-3 pb-3 border-b border-white/10">
                    <div className="mt-1 rounded-lg bg-[#e1e65c]/10 p-2.5">
                      <Icon className="h-5 w-5 text-[#e1e65c]" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-base font-bold text-white mb-1">
                        {navItem.title}
                      </h4>
                      <p className="text-sm text-zinc-400 leading-relaxed">
                        {navItem.description}
                      </p>
                    </div>
                  </div>

                  {/* Links */}
                  <ul className="space-y-1">
                    {navItem.items.map((item) => (
                      <ListItem
                        key={item.title}
                        title={item.title}
                        href={item.href}
                        description={item.description}
                      />
                    ))}
                  </ul>

                  {/* Footer */}
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <a
                      href={navItem.href}
                      onClick={(e) => {
                        e.preventDefault();
                        navigate(navItem.href);
                      }}
                      className="inline-flex items-center text-xs text-[#e1e65c] hover:text-[#d4d950] transition-colors font-medium group"
                    >
                      View all
                      <svg
                        className="ml-1 h-3 w-3 transition-transform group-hover:translate-x-0.5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </a>
                  </div>
                </div>
              </NavigationMenuContent>
            </NavigationMenuItem>
          );
        })}
      </NavigationMenuList>
    </NavigationMenu>
  );
}
