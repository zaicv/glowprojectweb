// no change to imports
import { IconContainer } from "@tabler/icons-react";
import { cn } from "../../lib/utils";
import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  type MotionValue,
} from "motion/react";
import { useRef, useState } from "react";

export const FloatingDock = ({
  items,
  className,
  theme,
  visible,
}: {
  items: { title: string; icon: React.ReactNode; href: string }[];
  className?: string;
  theme: "light" | "dark" | "system";
  visible: boolean;
}) => {
  const mouseX = useMotionValue(Infinity);

  const handleTouchMove = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    if (touch) mouseX.set(touch.clientX);
  };

  const handleTouchEnd = () => {
    mouseX.set(Infinity);
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.7, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.7, y: 50 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          onMouseMove={(e) => mouseX.set(e.pageX)}
          onMouseLeave={() => mouseX.set(Infinity)}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          className={cn(
            `fixed bottom-24 right-6 z-[60] flex flex-col items-center gap-3 rounded-full px-3 py-2 ${
              theme === "dark" ? "bg-[#1a1a1a]/80 backdrop-blur-md" : "bg-white/80 backdrop-blur-md"
            } shadow-2xl`,
            className
          )}
        >
          {items.map((item) => (
            <IconContainer
              mouseX={mouseX}
              key={item.title}
              {...item}
              theme={theme}
            />
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
};