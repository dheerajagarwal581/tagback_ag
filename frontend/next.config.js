/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // In production on Render, proxy /api/v1 calls to the backend service.
    // In local development, proxy to localhost:8000.
    const backendUrl =
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === "production"
        ? "https://qr-lost-found-backend.onrender.com"
        : "http://localhost:8000");

    const cleanBackend = backendUrl
      .replace(/\/+$/, "")
      .replace(/\/api\/v1\/?$/, "");

    return [
      {
        source: "/api/v1/:path*",
        destination: `${cleanBackend}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
