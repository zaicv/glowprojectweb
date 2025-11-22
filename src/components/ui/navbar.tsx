import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface NavbarsProps {
  children: ReactNode;
  className?: string;
}

export function Navbar({ children, className }: NavbarsProps) {
  return (
    <nav className={cn("flex items-center justify-between", className)}>
      {children}
    </nav>
  );
}

interface NavbarsSectionProps {
  children: ReactNode;
  className?: string;
}

export function NavbarsLeft({ children, className }: NavbarsSectionProps) {
  return (
    <div className={cn("flex items-center gap-6", className)}>
      {children}
    </div>
  );
}

export function NavbarsRight({ children, className }: NavbarsSectionProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {children}
    </div>
  );
}

