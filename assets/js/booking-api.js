import { API_BASE_URL } from "./config.js";

export async function cancelBookingRequest(eventId) {
  const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/book`, {
    method: "DELETE",
    credentials: "include",
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "Unable to cancel booking.");
  }

  return result;
}
