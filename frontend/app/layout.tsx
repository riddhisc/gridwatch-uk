import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: "Green Power Hours",
  description: "See when UK electricity is greener and cheaper",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-GB">
      <body>
        <div className="flex min-h-screen flex-col">
          <SiteHeader />
          <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
            {children}
          </main>
          <footer className="mt-auto border-t border-slate-200 bg-white">
            <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500 sm:px-6">
              Live data from NESO Carbon Intensity and Octopus Energy. Not an official government service.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}
