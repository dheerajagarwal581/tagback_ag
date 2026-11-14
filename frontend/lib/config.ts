// Centralized API and WebSocket configuration for both Local Dev and Render Production

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    // In browser: if deployed on Render or any remote domain, use same-origin relative path "/api/v1".
    // Next.js rewrites in next.config.js will reverse-proxy this to the backend automatically!
    // This gives ZERO CORS errors, ZERO Mixed Content blocks, and 100% reliable First-Party cookies.
    if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
      return "/api/v1";
    }
  }

  // Local development fallback
  if (process.env.NEXT_PUBLIC_API_URL) {
    let url = process.env.NEXT_PUBLIC_API_URL.trim().replace(/\/+$/, "");
    if (!url.endsWith("/api/v1")) {
      url = `${url}/api/v1`;
    }
    return url;
  }

  return "http://localhost:8000/api/v1";
}

export function getWsBaseUrl(): string {
  if (typeof window !== "undefined") {
    if (process.env.NEXT_PUBLIC_WS_URL) {
      let ws = process.env.NEXT_PUBLIC_WS_URL.trim();
      if (!ws.startsWith("ws://") && !ws.startsWith("wss://")) {
        ws = `wss://${ws}`;
      }
      return ws.replace(/\/+$/, "");
    }

    if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
      const hostname = window.location.hostname;
      const backendHost = hostname.replace("frontend", "backend");
      return `wss://${backendHost}/api/v1/ws`;
    }
  }

  return "ws://localhost:8000/api/v1/ws";
}

// Proxied string-like constants that evaluate dynamically at runtime when string-interpolated:
export const API_BASE_URL = {
  toString: () => getApiBaseUrl(),
  valueOf: () => getApiBaseUrl(),
} as unknown as string;

export const WS_BASE_URL = {
  toString: () => getWsBaseUrl(),
  valueOf: () => getWsBaseUrl(),
} as unknown as string;
