import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QR Lost & Found | Privacy-Preserving Temporary Communication",
  description: "Contact the owner of a lost item safely and anonymously without exchanging phone numbers or email addresses.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col font-sans">
        <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold text-lg text-slate-900">
              <span className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-black">
                QR
              </span>
              <span>Lost & Found</span>
            </a>
            <nav className="flex items-center gap-4">
              <a
                href="/login"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Owner Login
              </a>
              <a
                href="/register"
                className="text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded-lg transition-colors shadow-sm"
              >
                Get Your QR
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-sm text-slate-500">
          <p>QR Temporary Communication & Lost-and-Found Platform. Privacy First.</p>
        </footer>
      </body>
    </html>
  );
}
