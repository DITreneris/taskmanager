import { useNavigate } from "react-router-dom";
import { Button } from "components/Button";

export default function App() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-center mb-4">
              Tempo
            </h1>
            
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center w-full">
              <Button size="lg" onClick={() => navigate("/calendar")}> 
                View Calendar
              </Button>
              <Button size="lg" onClick={() => navigate("/emails")} variant="outline">
                Check Emails
              </Button>
            </div>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-12 sm:px-6 lg:px-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Smart Scheduling At Your Fingertips</h2>
              <p className="text-lg text-gray-600 mb-6">
                Tempo automates scheduling by scanning emails, managing your calendar, and suggesting alternatives when conflicts arise.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium mb-2">Email Parsing</h3>
                  <p className="text-sm">Scans incoming emails for meeting requests and automatically extracts dates and times.</p>
                </div>
                
                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium mb-2">Calendar Management</h3>
                  <p className="text-sm">Checks your calendar for availability and reserves time slots for tentative meetings.</p>
                </div>
                
                <div className="bg-purple-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium mb-2">Smart Suggestions</h3>
                  <p className="text-sm">When conflicts arise, suggests alternative times based on your availability.</p>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={() => navigate("/calendar")} 
                  size="lg"
                >
                  View Calendar
                </Button>
                <Button 
                  onClick={() => navigate("/emails")} 
                  variant="outline"
                  size="lg"
                >
                  Check Emails
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
