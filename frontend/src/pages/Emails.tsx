import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import brain from "brain";
import { Button } from "components/Button";
import { EmailMessage } from "types";

export default function Emails() {
  const navigate = useNavigate();
  const [emails, setEmails] = useState<EmailMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"all" | "meetings">("meetings");
  const [meetingRequests, setMeetingRequests] = useState<any[]>([]);

  const fetchEmails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await brain.scan_emails({ max_results: 30 });
      const data: EmailMessage[] = await response.json();
      setEmails(data);
    } catch (err) {
      console.error("Error fetching emails:", err);
      setError("Failed to load emails");
    } finally {
      setLoading(false);
    }
  };

  const fetchMeetingRequests = async () => {
    try {
      const response = await brain.get_meeting_requests();
      const data = await response.json();
      setMeetingRequests(data);
    } catch (err) {
      console.error("Error fetching meeting requests:", err);
    }
  };

  useEffect(() => {
    // Check auth status first
    const checkAuth = async () => {
      try {
        const response = await brain.auth_status();
        const data = await response.json();
        if (!data.is_authenticated) {
          navigate("/gmail-auth");
          return;
        }
        // If authenticated, fetch data
        await Promise.all([fetchEmails(), fetchMeetingRequests()]);
      } catch (err) {
        console.error("Error checking auth:", err);
        navigate("/gmail-auth");
      }
    };

    checkAuth();
  }, [navigate]);

  const formatDateTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch (e) {
      return dateStr;
    }
  };

  const displayedEmails = activeTab === "meetings" 
    ? emails.filter((email) => email.contains_meeting_request)
    : emails;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Email Scanner</h1>
        <div className="space-x-2">
          <Button
            onClick={fetchEmails}
            disabled={loading}
            variant="outline"
            size="sm"
          >
            {loading ? "Scanning..." : "Scan Now"}
          </Button>
          <Button 
            onClick={() => navigate("/gmail-auth")} 
            variant="outline"
            size="sm"
          >
            Gmail Settings
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab("meetings")}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${activeTab === "meetings" 
                ? "border-blue-500 text-blue-600" 
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"}`}
            >
              Meeting Requests
            </button>
            <button
              onClick={() => setActiveTab("all")}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${activeTab === "all" 
                ? "border-blue-500 text-blue-600" 
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"}`}
            >
              All Scanned Emails
            </button>
          </nav>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : displayedEmails.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-500">
              {activeTab === "meetings" 
                ? "No meeting requests found in your recent emails." 
                : "No emails have been scanned yet."}
            </p>
            <Button onClick={fetchEmails} className="mt-4">
              Scan Emails Now
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    From
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  {activeTab === "meetings" && (
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Detected Times
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayedEmails.map((email) => (
                  <tr key={email.message_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {email.sender}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{email.subject}</div>
                      <div className="text-xs text-gray-500 mt-1 line-clamp-2">{email.snippet}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDateTime(email.date)}
                    </td>
                    {activeTab === "meetings" && (
                      <td className="px-6 py-4">
                        {email.detected_dates.length > 0 && email.detected_times.length > 0 ? (
                          <div>
                            <div className="text-xs font-medium text-gray-900">Dates:</div>
                            <div className="text-xs text-gray-600">
                              {email.detected_dates.slice(0, 3).join(", ")}
                              {email.detected_dates.length > 3 && "..."}
                            </div>
                            <div className="text-xs font-medium text-gray-900 mt-1">Times:</div>
                            <div className="text-xs text-gray-600">
                              {email.detected_times.slice(0, 3).join(", ")}
                              {email.detected_times.length > 3 && "..."}
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-500">None detected</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {activeTab === "meetings" && meetingRequests.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Processed Meeting Requests</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      From
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subject
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proposed Time
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {meetingRequests.map((request) => (
                    <tr key={request.message_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {request.sender}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{request.subject}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {request.proposed_datetime ? (
                          formatDateTime(request.proposed_datetime)
                        ) : (
                          <span className="text-xs italic">Not determined</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${{
                          pending: "bg-yellow-100 text-yellow-800",
                          confirmed: "bg-green-100 text-green-800",
                          declined: "bg-red-100 text-red-800",
                          suggested_alternative: "bg-blue-100 text-blue-800"
                        }[request.status]}`}>
                          {request.status.charAt(0).toUpperCase() + request.status.slice(1).replace("_", " ")}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
