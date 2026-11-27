import { API_BASE_URL } from "./config.js";

export async function getCurrentMember() {
  const response = await fetch(`${API_BASE_URL}/api/me`, {
    method: "GET",
    credentials: "include",
  });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Authentication request failed: ${response.status}`);
  }

  return await response.json();
}
