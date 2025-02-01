import { CalendarIcon, Clock, Plus } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card"
import { Button } from "~/components/ui/button"
import { Calendar } from "~/components/ui/calendar"

const appointments = [
  { date: "2023-06-01", time: "09:00 AM", description: "Dental check-up", doctor: "Dr. Brown" },
  { date: "2023-06-15", time: "02:30 PM", description: "Eye examination", doctor: "Dr. Davis" },
  { date: "2023-06-28", time: "11:00 AM", description: "Physical therapy", doctor: "Dr. Wilson" },
]

export default function SchedulePage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Schedule</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" /> New Appointment
        </Button>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Calendar</CardTitle>
            <CardDescription>View and manage your appointments</CardDescription>
          </CardHeader>
          <CardContent>
            <Calendar />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Appointments</CardTitle>
            <CardDescription>Your scheduled medical appointments</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {appointments.map((appointment, index) => (
                <li key={index} className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <CalendarIcon className="h-6 w-6 text-blue-500 mt-1" />
                  <div>
                    <p className="font-medium">{appointment.description}</p>
                    <p className="text-sm text-gray-500">Date: {appointment.date}</p>
                    <p className="text-sm text-gray-500">Time: {appointment.time}</p>
                    <p className="text-sm text-gray-500">Doctor: {appointment.doctor}</p>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full">
              <Clock className="mr-2 h-4 w-4" /> View All Appointments
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

