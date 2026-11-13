// Centralized API and WebSocket configuration for both Local Dev and Render Production

function resolveApiBaseUrl(): string {
  let url = process.env.NEXT_PUBLIC_API_URL;

  // If unset, detect if running in browser on Render
  if (!url) {
    if (typeof window !== "undefined") {
      const hostname = window.location.hostname;
      if (hostname.includes("onrender.com")) {
        // Automatically map frontend service to backend service
        // e.g. qr-lost-found-frontend.onrender.com -> qr-lost-found-backend.onrender.com
        const backendHost = hostname.replace("frontend", "backend");
        return `https://${backendHost}/api/v1`;
      }
    }
    return "http://localhost:8000/api/v1";
  }

  url = url.trim();

  // If Render passed just a raw service name (e.g. "qr-lost-found-backend")
  if (!url.includes(".") && !url.includes("localhost")) {
    url = `${url}.onrender.com`;
  }

  // Ensure scheme
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = `https://${url}`;
  }

  // Remove trailing slashes
  url = url.replace(/\/+$/, "");

  // Ensure path ends with /api/v1
  if (!url.endsWith("/api/v1")) {
    url = `${url}/api/v1`;
  }

  return url;
}

function resolveWsBaseUrl(): string {
  let wsUrl = process.env.NEXT_PUBLIC_WS_URL;

  if (!wsUrl) {
    const apiUrl = resolveApiBaseUrl();
    if (apiUrl.startsWith("https://")) {
      return apiUrl.replace("https://", "wss://").replace(/\/api\/v1$/, "/api/v1/ws");
    }
    return apiUrl.replace("http://", "ws://").replace(/\/api\/v1$/, "/api/v1/ws");
  }

  wsUrl = wsUrl.trim();

  if (!wsUrl.includes(".") && !wsUrl.includes("localhost")) {
    wsUrl = `${wsUrl}.onrender.com`;
  }

  if (!wsUrl.startsWith("ws://") && !wsUrl.startsWith("wss://")) {
    wsUrl = `wss://${wsUrl}`;
  }

  wsUrl = wsUrl.replace(/\/+$/, "");
  if (!wsUrl.endsWith("/api/v1/ws")) {
    if (wsUrl.endsWith("/api/v1")) {
      wsUrl = `${wsUrl}/ws`;
    } else {
      wsUrl = `${wsUrl}/api/v1/ws`;
    }
  }

  return wsUrl;
}

export const API_BASE_URL = resolveApiBaseUrl();
export const WS_BASE_URL = resolveWsBaseUrl();
