import { Plus } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Button } from "~/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table"

const medications = [
  { name: "Aspirin", dosage: "100mg", frequency: "Once daily" },
  { name: "Lisinopril", dosage: "10mg", frequency: "Twice daily" },
  { name: "Metformin", dosage: "500mg", frequency: "With meals" },
]

export default function MedicationsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Medications</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" /> Add Medication
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Current Medications</CardTitle>
          <CardDescription>List of your prescribed medications</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Dosage</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {medications.map((med) => (
                <TableRow key={med.name}>
                  <TableCell className="font-medium">{med.name}</TableCell>
                  <TableCell>{med.dosage}</TableCell>
                  <TableCell>{med.frequency}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      Edit
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-500">
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

