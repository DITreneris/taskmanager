import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import brain from "brain";
import { CalendarEvent, TimeSlot } from "brain/data-contracts";
import { Button } from "components/Button";
import { EventForm } from "components/EventForm";

export default function Calendar() {
  const navigate = useNavigate();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0] // Today's date in YYYY-MM-DD format
  );
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [duration, setDuration] = useState(30); // Default 30 min meeting
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [showEventForm, setShowEventForm] = useState(false);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await brain.list_events();
      const data: CalendarEvent[] = await response.json();
      setEvents(data);
    } catch (e) {
      console.error("Error fetching events:", e);
      setError("Failed to load calendar events");
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableSlots = async () => {
    try {
      setSlotsLoading(true);
      const response = await brain.get_available_slots({
        date: selectedDate,
        duration_minutes: duration
      });
      const data: TimeSlot[] = await response.json();
      setAvailableSlots(data);
    } catch (e) {
      console.error("Error fetching available slots:", e);
      setError("Failed to load available time slots");
    } finally {
      setSlotsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleFindSlots = () => {
    fetchAvailableSlots();
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
    setAvailableSlots([]); // Clear previous slots
  };

  const handleDurationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setDuration(parseInt(e.target.value));
    setAvailableSlots([]); // Clear previous slots
  };

  const handleCreateEvent = async (eventData: Omit<CalendarEvent, "id">) => {
    try {
      // Add UUID for the event
      const eventWithId: CalendarEvent = {
        ...eventData,
        id: crypto.randomUUID() // Using native crypto.randomUUID instead of uuid package
      };

      const response = await brain.create_event(eventWithId);
      await response.json();
      
      // Refresh events list
      fetchEvents();
      setShowEventForm(false);
    } catch (e) {
      console.error("Error creating event:", e);
      
      // Check if it's a conflict error
      if (e instanceof Error && e.message.includes("conflict")) {
        // Get the date from the event to suggest alternatives
        const eventDate = new Date(eventData.start_time).toISOString().split('T')[0];
        
        try {
          // Get event duration in minutes
          const start = new Date(eventData.start_time);
          const end = new Date(eventData.end_time);
          const durationMs = end.getTime() - start.getTime();
          const durationMinutes = Math.round(durationMs / 60000);
          
          // Request alternative times
          const suggestResponse = await brain.suggest_alternative_times({
            date: eventDate,
            duration_minutes: durationMinutes
          });
          
          const alternativeTimes = await suggestResponse.json();
          
          if (alternativeTimes && alternativeTimes.length > 0) {
            setAvailableSlots(alternativeTimes);
            setSelectedDate(eventDate);
            setDuration(durationMinutes);
            setError("There's a scheduling conflict. Here are some alternative time slots.");
            setShowEventForm(false);
            return;
          }
        } catch (suggestErr) {
          console.error("Error suggesting alternatives:", suggestErr);
        }
      }
      
      setError("Failed to create event. Please try again.");
    }
  };

  function formatDateTime(dateTimeStr: string): string {
    try {
      const date = new Date(dateTimeStr);
      return date.toLocaleString();
    } catch (e) {
      return dateTimeStr;
    }
  }
  
  function formatTime(dateTimeStr: string): string {
    try {
      const date = new Date(dateTimeStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return dateTimeStr;
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Calendar</h1>
        <div className="space-x-2">
          <Button
            onClick={() => setShowEventForm(true)}
            size="sm"
          >
            Add Event
          </Button>
          <Button
            onClick={() => navigate("/emails")}
            variant="outline"
            size="sm"
          >
            Email Scanner
          </Button>
          <Button 
            onClick={() => navigate("/")} 
            variant="outline"
            size="sm"
          >
            Home
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Event Form */}
        {showEventForm && (
          <div className="md:col-span-3 mb-6">
            <EventForm 
              onCreateEvent={handleCreateEvent}
              onCancel={() => setShowEventForm(false)} 
            />
          </div>
        )}
        
        {/* Calendar Events */}
        <div className="md:col-span-2">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="border-b border-gray-200 px-6 py-4">
              <h2 className="text-lg font-medium">Your Schedule</h2>
            </div>
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : events.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-gray-500">No events scheduled</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {events
                  .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
                  .map((event) => (
                    <div key={event.id} className="p-6 hover:bg-gray-50">
                      <div className="flex justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{event.title}</h3>
                          {event.description && (
                            <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                          )}
                        </div>
                        <span 
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            event.status === "confirmed" ? "bg-green-100 text-green-800" :
                            event.status === "tentative" ? "bg-yellow-100 text-yellow-800" :
                            "bg-red-100 text-red-800"
                          }`}
                        >
                          {event.status?.charAt(0).toUpperCase() + event.status?.slice(1) || "Unknown"}
                        </span>
                      </div>
                      <div className="mt-2 text-sm text-gray-500">
                        {formatDateTime(event.start_time)} - {formatTime(event.end_time)}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>

        {/* Available Slots */}
        <div>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="border-b border-gray-200 px-6 py-4">
              <h2 className="text-lg font-medium">Find Available Slots</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label htmlFor="date" className="block text-sm font-medium text-gray-700">Date</label>
                  <input
                    type="date"
                    id="date"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    value={selectedDate}
                    onChange={handleDateChange}
                  />
                </div>
                <div>
                  <label htmlFor="duration" className="block text-sm font-medium text-gray-700">Meeting Duration</label>
                  <select
                    id="duration"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    value={duration}
                    onChange={handleDurationChange}
                  >
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="45">45 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="90">1.5 hours</option>
                    <option value="120">2 hours</option>
                  </select>
                </div>
                <Button
                  onClick={handleFindSlots}
                  className="w-full"
                  disabled={slotsLoading}
                >
                  {slotsLoading ? "Finding slots..." : "Find Available Slots"}
                </Button>
              </div>

              {availableSlots.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Available Time Slots:</h3>
                  <div className="space-y-2">
                    {availableSlots.map((slot, index) => (
                      <div key={index} className="p-3 bg-blue-50 rounded-md">
                        <p className="text-sm font-medium text-blue-800">
                          {formatTime(slot.start)} - {formatTime(slot.end)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {availableSlots.length === 0 && !slotsLoading && (
                <div className="mt-6 text-center text-sm text-gray-500">
                  Select a date and duration, then click "Find Available Slots"
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}