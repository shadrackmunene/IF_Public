import type { Metadata } from "next";
import "./globals.css";
import TopBar from "@/components/TopBar";
import { DataProvider } from "@/components/DataProvider";

export const metadata: Metadata = {
  title: "Youth Livelihoods",
  description: "Real Livelihoods youth segmentation: six segments of Kenyan youth, their profiles and a self-assessment.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <TopBar />
        <DataProvider>{children}</DataProvider>
      </body>
    </html>
  );
}
