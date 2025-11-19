"use client";

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import clsx from "clsx";

type Card = {
  title: string;
  src: string;
  href: string;
};

export function FocusCards({ cards }: { cards: Card[] }) {
  const [hovered, setHovered] = useState<number | null>(null);
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-2 grid-rows-2 gap-3 w-full h-screen p-3">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          onMouseEnter={() => setHovered(index)}
          onMouseLeave={() => setHovered(null)}
          onClick={() => router.push(card.href)}
          className={clsx(
            "relative rounded-xl overflow-hidden transition-all duration-300 ease-out shadow-lg",
            hovered !== null && hovered !== index && "blur-sm scale-[0.98]"
          )}
        >
          <img
            src={card.src}
            alt={card.title}
            className="object-cover absolute inset-0 w-full h-full"
          />
          <div
            className={clsx(
              "absolute inset-0 bg-black/40 flex items-center justify-center transition-opacity duration-300",
              hovered === index ? "opacity-100" : "opacity-0"
            )}
          >
            <h2 className="text-white text-2xl font-semibold">{card.title}</h2>
          </div>
        </motion.div>
      ))}
    </div>
  );
}