import { useEffect, useRef } from "react";

function useSidebarSwipe({ onSwipeLeft }: { onSwipeLeft: () => void }) {
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  const touchInProgress = useRef(false);

  useEffect(() => {
    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      touchStart.current = { x: touch.clientX, y: touch.clientY };
      touchInProgress.current = true;
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!touchStart.current || !touchInProgress.current) return;

      const touch = e.touches[0];
      const dx = touch.clientX - touchStart.current.x;
      const dy = touch.clientY - touchStart.current.y;

      // Require a minimum horizontal swipe distance (more than vertical) to register
      const horizontalThreshold = 80;
      const verticalThreshold = 60;

      const isHorizontalSwipe =
        Math.abs(dx) > horizontalThreshold && Math.abs(dx) > Math.abs(dy);
      const isVerticalScroll = Math.abs(dy) > verticalThreshold;

      if (isVerticalScroll) {
        touchInProgress.current = false; // cancel swipe if vertical scroll is likely
        return;
      }

      if (isHorizontalSwipe && dx < 0) {
        onSwipeLeft();
        touchInProgress.current = false;
        touchStart.current = null;
      }
    };

    const handleTouchEnd = () => {
      touchInProgress.current = false;
      touchStart.current = null;
    };

    window.addEventListener("touchstart", handleTouchStart, { passive: true });
    window.addEventListener("touchmove", handleTouchMove, { passive: true });
    window.addEventListener("touchend", handleTouchEnd);

    return () => {
      window.removeEventListener("touchstart", handleTouchStart);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    };
  }, [onSwipeLeft]);
}

export default useSidebarSwipe;
