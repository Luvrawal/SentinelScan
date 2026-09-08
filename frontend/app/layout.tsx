import "./globals.css";

export const metadata = { title: "SentinelScan", description: "Website vulnerability scanning" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
