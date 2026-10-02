import type { Metadata } from "next";

import "./styles.css";

export const metadata: Metadata = {
  title: "QuickNote",
  description: "Personal notes organization and management system",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg"
  },
  appleWebApp: {
    capable: true,
    title: "QuickNote"
  }
};

export const viewport = {
  themeColor: "#e85d9f"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
