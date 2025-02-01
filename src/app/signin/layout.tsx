import "@/styles/globals.css"
import { GeistSans } from "geist/font/sans"
import { cn } from "@/lib/utils"
import type React from "react"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn("min-h-screen bg-background font-sans antialiased", GeistSans.className)}>{children}</body>
    </html>
  )
}



import './globals.css'