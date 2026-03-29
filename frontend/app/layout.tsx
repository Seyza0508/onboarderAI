import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "OnboardAI",
  description: "Agentic Developer Onboarding Assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <h1 className="text-lg font-semibold">OnboardAI</h1>
            <nav className="flex gap-4 text-sm">
              <Link href="/auth" className="hover:underline">
                Auth
              </Link>
              <Link href="/intake" className="hover:underline">
                Intake
              </Link>
              <Link href="/assistant" className="hover:underline">
                Assistant
              </Link>
              <Link href="/dashboard" className="hover:underline">
                Dashboard
              </Link>
              <Link href="/manager" className="hover:underline">
                Manager
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
