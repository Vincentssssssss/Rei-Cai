import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PPT Translator BS MVP",
  description: "FastAPI + Next.js PPT translation tool"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
