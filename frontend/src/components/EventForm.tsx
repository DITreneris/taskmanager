import React, { useState } from "react";
import { CalendarEvent } from "brain/data-contracts";
import { Button } from "components/Button";

interface EventFormProps {
  onCreateEvent: (event: Omit<CalendarEvent, "id">) => Promise<void>;
  onCancel: () => void;
}

export function EventForm({ onCreateEvent, onCancel }: EventFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endDate, setEndDate] = useState("");
  const [endTime, setEndTime] = useState("");
  const [status, setStatus] = useState<"confirmed" | "tentative">("confirmed");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    if (!title) {
      setError("Title is required");
      return;
    }

    if (!startDate || !startTime) {
      setError("Start date and time are required");
      return;
    }

    if (!endDate || !endTime) {
      setError("End date and time are required");
      return;
    }

    const startDateTime = new Date(`${startDate}T${startTime}:00`);
    const endDateTime = new Date(`${endDate}T${endTime}:00`);

    if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
      setError("Invalid date or time format");
      return;
    }

    if (endDateTime <= startDateTime) {
      setError("End time must be after start time");
      return;
    }

    try {
      setIsSubmitting(true);

      // Create event object
      const newEvent: Omit<CalendarEvent, "id"> = {
        title,
        description: description || undefined,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        is_all_day: false,
        status,
        source: "manual"
      };

      await onCreateEvent(newEvent);
    } catch (err) {
      console.error("Error creating event:", err);
      setError(err instanceof Error ? err.message : "Failed to create event");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-medium mb-4">Create New Event</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Title
          </label>
          <input
            type="text"
            id="title"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description (optional)
          </label>
          <textarea
            id="description"
            rows={3}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
              Start Date
            </label>
            <input
              type="date"
              id="startDate"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                if (!endDate) setEndDate(e.target.value);
              }}
              required
            />
          </div>

          <div>
            <label htmlFor="startTime" className="block text-sm font-medium text-gray-700">
              Start Time
            </label>
            <input
              type="time"
              id="startTime"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
              End Date
            </label>
            <input
              type="date"
              id="endDate"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="endTime" className="block text-sm font-medium text-gray-700">
              End Time
            </label>
            <input
              type="time"
              id="endTime"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            id="status"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={status}
            onChange={(e) => setStatus(e.target.value as "confirmed" | "tentative")}
          >
            <option value="confirmed">Confirmed</option>
            <option value="tentative">Tentative</option>
          </select>
        </div>

        <div className="flex justify-end space-x-3 pt-3">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create Event"}
          </Button>
        </div>
      </form>
    </div>
  );
}
