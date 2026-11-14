/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    let target = (
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      ""
    ).trim();

    if (!target) {
      target =
        process.env.NODE_ENV === "production"
          ? "https://qr-lost-found-backend.onrender.com"
          : "http://localhost:8000";
    }

    // If Render passed just the service name (e.g. "qr-lost-found-backend")
    if (!target.includes(".") && !target.includes("localhost")) {
      target = `https://${target}.onrender.com`;
    }

    // Next.js strictly requires destination to start with http://, https://, or /
    if (!target.startsWith("http://") && !target.startsWith("https://")) {
      target = `https://${target}`;
    }

    const cleanBackend = target
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
