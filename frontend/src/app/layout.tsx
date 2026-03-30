"use client";
import "./globals.css";
import { useEffect } from "react";
import { handleRedirectPromise } from "@/lib/cognito";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Process B2C redirect on every page load (safe to call multiple times)
    handleRedirectPromise().catch(console.error);
  }, []);

  return (
    <html lang="pt">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
