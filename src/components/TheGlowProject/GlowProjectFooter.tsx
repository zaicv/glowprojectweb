import { Link } from "react-router-dom";
import { Mail } from "lucide-react";

const footerColumns = [
  {
    title: "Explore",
    links: [
      { label: "The Glow Foundation", href: "/the-glow-foundation" },
      { label: "Glow Process", href: "/glow-process" },
      { label: "GlowGPT", href: "/glowgpt" },
      { label: "ARSA Foundation", href: "/arsafoundation" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Healing Framework", href: "/glow-process" },
      { label: "AI Tools", href: "/glowgpt" },
      { label: "Community Care", href: "/arsafoundation" },
      { label: "About The Glow", href: "/about" },
    ],
  },
  {
    title: "Connect",
    links: [
      { label: "Join the Movement", href: "/the-glow-foundation" },
      { label: "Stories & Research", href: "/arsafoundation" },
      { label: "GlowGPT Updates", href: "/glowgpt" },
      { label: "Contact", href: "mailto:hello@theglowproject.com" },
    ],
  },
];

export function GlowProjectFooter() {
  return (
    <footer className="bg-white px-6 py-16">
      <div className="mx-auto max-w-6xl space-y-12 border-t border-gray-200 pt-12">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-gray-500">
              The Glow Project
            </p>
            <h3 className="mt-2 text-3xl font-semibold text-black">
              Return to the Glow
            </h3>
            <p className="mt-3 max-w-xl text-sm text-gray-600">
              Emotional, spiritual, and physical healing through conscious tech
              and community care.
            </p>
          </div>
          <Link
            to="/glow-process"
            className="inline-flex items-center justify-center rounded-full border border-black/10 bg-black px-8 py-3 text-sm font-medium text-white transition hover:bg-black/80"
          >
            Start the Process
          </Link>
        </div>

        <div className="grid gap-10 md:grid-cols-4">
          <div className="space-y-4">
            <p className="text-sm font-semibold text-black">Contact</p>
            <a
              href="mailto:hello@theglowproject.com"
              className="flex items-center gap-2 text-sm text-gray-600 transition hover:text-black"
            >
              <Mail className="h-4 w-4" />
              hello@theglowproject.com
            </a>
            <p className="text-sm text-gray-500">
              Serving the community online and across the ARSA network.
            </p>
          </div>

          {footerColumns.map((column) => (
            <div key={column.title} className="space-y-4">
              <p className="text-sm font-semibold text-black">
                {column.title}
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                {column.links.map((link) =>
                  link.href.startsWith("mailto:") ? (
                    <li key={link.label}>
                      <a
                        href={link.href}
                        className="transition hover:text-black"
                      >
                        {link.label}
                      </a>
                    </li>
                  ) : (
                    <li key={link.label}>
                      <Link
                        to={link.href}
                        className="transition hover:text-black"
                      >
                        {link.label}
                      </Link>
                    </li>
                  )
                )}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-gray-200 pt-8 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} The Glow Project. A house for anyone
          returning from Chaos to The Glow.
        </div>
      </div>
    </footer>
  );
}
