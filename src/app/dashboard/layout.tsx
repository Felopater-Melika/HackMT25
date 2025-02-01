import type { ReactNode } from "react"
import Link from "next/link"
import { UserCircle } from "lucide-react"
import { Button } from "~/components/ui/button"

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link href="/dashboard" className="flex-shrink-0 flex items-center">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">InsideBox</span>
              </Link>
            </div>
            <div className="flex items-center">
              <Button variant="ghost" size="sm">
                <UserCircle className="mr-2 h-4 w-4" />
                Profile
              </Button>
              <Button variant="ghost" size="sm">
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  )
}

