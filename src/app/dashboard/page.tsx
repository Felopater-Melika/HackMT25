import Link from "next/link"
import { UserCircle, PillIcon, ClipboardList, Calendar } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card"
import { Button } from "~/components/ui/button"

export default function DashboardPage() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
          <CardDescription>Your personal information</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <UserCircle className="h-12 w-12 text-gray-400" />
            <div>
              <p className="text-lg font-medium">John Doe</p>
              <p className="text-sm text-gray-500">john.doe@example.com</p>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button variant="outline" size="sm">
            Edit Profile
          </Button>
        </CardFooter>
      </Card>

      <Link href="/dashboard/meds" passHref>
        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader>
            <CardTitle>Medications</CardTitle>
            <CardDescription>Manage your medications</CardDescription>
          </CardHeader>
          <CardContent>
            <PillIcon className="h-12 w-12 text-blue-500 mx-auto" />
          </CardContent>
          <CardFooter>
            <Button className="w-full">View Medications</Button>
          </CardFooter>
        </Card>
      </Link>

      <Link href="/dashboard/hist" passHref>
        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader>
            <CardTitle>History</CardTitle>
            <CardDescription>View your medical history</CardDescription>
          </CardHeader>
          <CardContent>
            <ClipboardList className="h-12 w-12 text-green-500 mx-auto" />
          </CardContent>
          <CardFooter>
            <Button className="w-full">View History</Button>
          </CardFooter>
        </Card>
      </Link>

      <Link href="/dashboard/schedule" passHref>
        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader>
            <CardTitle>Schedule</CardTitle>
            <CardDescription>Manage your appointments</CardDescription>
          </CardHeader>
          <CardContent>
            <Calendar className="h-12 w-12 text-purple-500 mx-auto" />
          </CardContent>
          <CardFooter>
            <Button className="w-full">View Schedule</Button>
          </CardFooter>
        </Card>
      </Link>
    </div>
  )
}

