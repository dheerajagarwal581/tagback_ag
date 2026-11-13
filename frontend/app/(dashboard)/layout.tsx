"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_BASE_URL } from "@/lib/config";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [owner, setOwner] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/auth/me`, {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => setOwner(data))
      .catch(() => router.push("/login"));
  }, [router]);

  const handleLogout = async () => {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    router.push("/login");
  };

  const navLinks = [
    { label: "Overview", href: "/dashboard" },
    { label: "My QR Code", href: "/dashboard/qr-code" },
    { label: "Pending Requests", href: "/dashboard/pending" },
    { label: "Active Chats", href: "/dashboard/active" },
    { label: "Recovered Items", href: "/dashboard/recovered" },
  ];

  return (
    <div className="flex-1 flex flex-col md:flex-row bg-slate-50 min-h-screen">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-white border-r border-slate-200 p-6 flex flex-col justify-between">
        <div>
          <div className="mb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Owner Account
            </h3>
            <p className="font-bold text-slate-900 truncate">
              {owner ? owner.display_name : "Loading..."}
            </p>
            <p className="text-xs text-slate-500 truncate">{owner?.email}</p>
          </div>

          <nav className="space-y-1">
            {navLinks.map((link) => {
              const active = pathname === link.href;
              return (
                <a
                  key={link.href}
                  href={link.href}
                  className={`block px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? "bg-emerald-50 text-emerald-800 font-semibold"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  {link.label}
                </a>
              );
            })}
          </nav>
        </div>

        <div className="pt-6 border-t border-slate-200 mt-6">
          <button
            onClick={handleLogout}
            className="w-full py-2 px-3 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg text-left transition-colors"
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-10">{children}</main>
    </div>
  );
}
