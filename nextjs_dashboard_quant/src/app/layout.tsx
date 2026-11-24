import type { Metadata } from "next";
import "./globals.css";
import TopBar from "@/components/TopBar";
import { DataProvider } from "@/components/DataProvider";

export const metadata: Metadata = {
  title: "Youth Livelihoods: Data",
  description: "Real Livelihoods youth segmentation data: how the six segments of Kenyan youth differ, by driver, pathway stage, county and survey question.",
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
