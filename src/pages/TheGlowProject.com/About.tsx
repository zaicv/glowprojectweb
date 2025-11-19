import { MorphingText } from '@/components/ui/morphing-text';

export default function PhilosophyPage() {
  const texts = [
    "hello",
    "Let Go of Your Chaos, Discover Your Peace.",
    "The Glow Project"
  ];

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <MorphingText 
        texts={texts}
        className="text-black"
      />
    </div>
  );
}