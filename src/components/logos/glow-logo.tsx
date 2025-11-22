import { Sun } from "lucide-react";

export default function GlowLogo({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <div className="flex items-center justify-center rounded-lg bg-[#e1e65c] p-1.5 shadow-sm">
      <Sun className={className} strokeWidth={2.5} fill="#000" />
    </div>
  );
}

