"use client";
import "./globals.css";
import { configureAmplify } from "@/lib/cognito";

configureAmplify();

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
