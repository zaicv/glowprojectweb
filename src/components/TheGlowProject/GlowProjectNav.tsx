import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import { Menu } from "lucide-react";
import { cn } from "@/lib/utils";

type NavItem = {
  label: string;
  href: string;
};

const navItems: NavItem[] = [
  { label: "Overview", href: "/the-glow-foundation" },
  { label: "The Glow Process", href: "/glow-process" },
  { label: "GlowGPT", href: "/glowgpt" },
  { label: "ARSA Foundation", href: "/arsafoundation" },
  { label: "About", href: "/the-glow-project" },
];

type GlowProjectNavProps = {
  ctaLabel?: string;
  ctaHref?: string;
};

export function GlowProjectNav({
  ctaLabel = "Get Started",
  ctaHref = "/glow-process",
}: GlowProjectNavProps) {
  const location = useLocation();

  const isActive = (href: string) =>
    location.pathname === href ||
    (href !== "/" && location.pathname.startsWith(`${href}/`));

  const navPill = (item: NavItem, active: boolean) => (
    <Link
      key={item.href}
      to={item.href}
      className={cn(
        "relative flex-1 rounded-full px-4 py-3 text-center text-sm font-medium transition-colors glass-hover",
        active ? "text-black" : "text-black hover:text-black"
      )}
    >
      <span className="relative z-10">{item.label}</span>
      {active && (
        <motion.span
          layoutId="glow-nav-pill"
          className="absolute inset-0 rounded-full bg-yellow-300/80 shadow-lg ring-1 ring-black/5"
          transition={{ type: "spring", stiffness: 350, damping: 30 }}
        />
      )}
    </Link>
  );

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-white/20 bg-transparent">
      <div className="mx-auto flex h-20 w-full items-center justify-between px-6 bg-liquid-glass glass-premium py-10 shadow-sm shadow-black/10">
        

        <div className=" mx-auto items-center gap-6 md:flex bg-transparent w-full">
        <Link
          to="/the-glow-foundation"
          className="flex items-center gap-3 rounded-3xl px-4 py-2   ring-white/60 transition hover:bg-white/70"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-300/80 text-black">
            <img src="/Branding Kit/PhoebeLogo.PNG" alt="The Glow Project" className="h-13 w-13 object-contain" />
          </div>
          <div className="text-left">
            <p className="text-xs uppercase tracking-[0.3em] text-gray-500">
              The Glow Project
            </p>
           
          </div>
        </Link>
          <div className="mx-auto relative flex w-[820px] items-center gap-1 rounded-full  p-1 ">
            {navItems.map((item) => navPill(item, isActive(item.href)))}
          </div>
          <Button
            asChild
            className="rounded-2xl bg-green-400 px-6 py-5 text-black shadow-lg shadow-black/20 transition glass-hover"
          >
            <Link to={ctaHref}>{ctaLabel}</Link>
          </Button>
        </div>

        <div className="md:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <button className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/60 bg-white/60 text-black shadow-md backdrop-blur-md">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </button>
            </SheetTrigger>
            <SheetContent
              side="right"
              className="w-full bg-white/90 sm:max-w-sm"
            >
              <SheetHeader className="mb-6 text-left">
                <SheetTitle className="flex items-center gap-2 text-xl font-semibold text-black">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#e1e65c] to-[#70ac85] text-black">
                    <img src="/Branding Kit/PhoebeLogo.PNG" alt="The Glow Project" className="h-5 w-5 object-contain" />
                  </div>
                  The Glow Project
                </SheetTitle>
                <p className="text-sm text-gray-500">
                  Navigate across the ecosystem
                </p>
              </SheetHeader>

              <div className="space-y-2">
                {navItems.map((item) => (
                  <SheetClose asChild key={item.href}>
                    <Link
                      to={item.href}
                      className={cn(
                        "flex items-center justify-between rounded-2xl border border-gray-200 px-4 py-3 text-base font-medium transition-colors",
                        isActive(item.href)
                          ? "bg-black text-white"
                          : "bg-white text-gray-700 hover:text-black"
                      )}
                    >
                      {item.label}
                      <span className="text-xs uppercase tracking-wider text-gray-400">
                        Go
                      </span>
                    </Link>
                  </SheetClose>
                ))}
              </div>

              <div className="mt-6">
                <SheetClose asChild>
                  <Button
                    asChild
                    className="w-full rounded-2xl bg-black py-6 text-base text-white hover:bg-black/80"
                  >
                    <Link to={ctaHref}>{ctaLabel}</Link>
                  </Button>
                </SheetClose>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
}
