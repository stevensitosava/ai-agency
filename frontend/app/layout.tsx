import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Agency · Multi-agent consulting system",
  description:
    "A virtual consulting agency staffed by AI agents. Researcher, Copywriter, Critic — bounded revision loop, structured deliverables, cited claims.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <header className="border-b border-rule">
          <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between text-sm">
            <Link
              href="/"
              className="font-serif italic font-semibold text-base text-ink hover:text-accent transition-colors"
            >
              AI Agency
            </Link>
            <nav className="flex items-center gap-6 text-ash">
              <Link href="/runs" className="hover:text-ink transition-colors">
                Runs
              </Link>
              <Link
                href="/evaluation"
                className="hover:text-ink transition-colors"
              >
                Eval
              </Link>
              <a
                href="https://github.com/stevensitosava/ai-agency"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-ink transition-colors"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-rule mt-16">
          <div className="max-w-5xl mx-auto px-6 py-6 text-xs text-mute flex flex-wrap gap-x-4 gap-y-2 justify-between">
            <span>
              Built by{" "}
              <a
                href="https://stevensawarin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-ash hover:text-ink transition-colors"
              >
                Steven Sawarin
              </a>{" "}
              · Tilburg, NL
            </span>
            <span className="font-mono">stevensitosava/ai-agency</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
