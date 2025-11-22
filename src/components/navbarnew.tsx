import { type VariantProps } from "class-variance-authority";
import { Menu } from "lucide-react";
import { ReactNode } from "react";

import { siteConfig } from "@/config/site";
import { cn } from "@/lib/utils";

import LaunchUI from "@/components/logos/launch-ui";
import { Button, buttonVariants } from "@/components/ui/button";
import {
    Navbars as NavbarsComponent,
    NavbarsLeft,
    NavbarsRight,
} from "@/components/ui/navbar";
import Navigation from "@/components/ui/navigation";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

interface NavbarLink {
  text: string;
  href: string;
}

interface NavbarActionProps {
  text: string;
  href: string;
  variant?: VariantProps<typeof buttonVariants>["variant"];
  icon?: ReactNode;
  iconRight?: ReactNode;
  isButton?: boolean;
}

interface NavbarProps {
  logo?: ReactNode;
  name?: string;
  homeUrl?: string;
  mobileLinks?: NavbarLink[];
  actions?: NavbarActionProps[];
  showNavigation?: boolean;
  customNavigation?: ReactNode;
  className?: string;
}

export default function NavbarNew({
  logo = <LaunchUI />,
  name = "Launch UI",
  homeUrl = siteConfig.url,
  mobileLinks = [
    { text: "Getting Started", href: siteConfig.url },
    { text: "Components", href: siteConfig.url },
    { text: "Documentation", href: siteConfig.url },
  ],
  actions = [
    { text: "Sign in", href: siteConfig.url, isButton: false },
    {
      text: "Get Started",
      href: siteConfig.url,
      isButton: true,
      variant: "default",
    },
  ],
  showNavigation = true,
  customNavigation,
  className,
}: NavbarProps) {
  return (
    <header className="fixed top-0 inset-x-0 z-50 flex justify-center px-4 pt-4">
      <div className="w-full max-w-7xl mx-auto relative">
        <div className={cn(
          "rounded-full px-6 py-3 border border-white/10 bg-zinc-900/70 shadow-[0_8px_30px_rgba(0,0,0,0.4)] backdrop-blur-2xl",
          className
        )}>
          <NavbarComponent className="rounded-full">
            <NavbarLeft>
              <a
                href={homeUrl}
                className="flex items-center gap-2 text-lg font-bold text-white hover:text-[#e1e65c] transition-colors"
              >
                {logo}
                <span className="hidden sm:inline">{name}</span>
              </a>
              {showNavigation && (customNavigation || <Navigation />)}
            </NavbarLeft>
          <NavbarRight>
            {actions.map((action, index) =>
              action.isButton ? (
                <Button
                  key={index}
                  variant={action.variant || "default"}
                  asChild
                  className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-full shadow-sm hidden sm:flex"
                >
                  <a href={action.href}>
                    {action.icon}
                    {action.text}
                    {action.iconRight}
                  </a>
                </Button>
              ) : (
                <a
                  key={index}
                  href={action.href}
                  className="hidden md:block text-sm text-zinc-300 hover:text-white transition-colors"
                >
                  {action.text}
                </a>
              ),
            )}
            <Sheet>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="shrink-0 md:hidden text-white hover:bg-white/10 rounded-full"
                >
                  <Menu className="size-5" />
                  <span className="sr-only">Toggle navigation menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="bg-zinc-900 border-zinc-800">
                <nav className="grid gap-6 text-lg font-medium">
                  <a
                    href={homeUrl}
                    className="flex items-center gap-2 text-xl font-bold text-white"
                  >
                    {logo}
                    <span>{name}</span>
                  </a>
                  {mobileLinks.map((link, index) => (
                    <a
                      key={index}
                      href={link.href}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      {link.text}
                    </a>
                  ))}
                  {actions.map((action, index) => (
                    <a
                      key={index}
                      href={action.href}
                      className="text-zinc-300 hover:text-white transition-colors"
                    >
                      {action.text}
                    </a>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
          </NavbarRight>
        </NavbarComponent>
        </div>
      </div>
    </header>
  );
}
