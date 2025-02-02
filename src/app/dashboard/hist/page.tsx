import { ClipboardList, Search } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"

const historyItems = [
  { date: "2023-05-15", description: "Annual check-up", doctor: "Dr. Smith" },
  { date: "2023-03-10", description: "Flu vaccination", doctor: "Dr. Johnson" },
  { date: "2023-01-22", description: "Blood test", doctor: "Dr. Williams" },
]

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Medical History</h1>
        <div className="flex items-center space-x-2">
          <Input placeholder="Search history..." />
          <Button size="icon">
            <Search className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Recent Medical Events</CardTitle>
          <CardDescription>Your recent medical history and appointments</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-4">
            {historyItems.map((item, index) => (
              <li key={index} className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <ClipboardList className="h-6 w-6 text-blue-500 mt-1" />
                <div>
                  <p className="font-medium">{item.description}</p>
                  <p className="text-sm text-gray-500">Date: {item.date}</p>
                  <p className="text-sm text-gray-500">Doctor: {item.doctor}</p>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

