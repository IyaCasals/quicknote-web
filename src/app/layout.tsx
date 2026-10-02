import type { Metadata } from "next";

import "./styles.css";

export const metadata: Metadata = {
  title: "QuickNote",
  description: "Personal notes organization and management system"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
