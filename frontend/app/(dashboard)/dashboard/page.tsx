"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";

export default function DashboardOverviewPage() {
  const [owner, setOwner] = useState<any>(null);
  const [counts, setCounts] = useState({ pending: 0, active: 0, recovered: 0 });

  useEffect(() => {
    fetch(`${API_BASE_URL}/auth/me`, { credentials: "include" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setOwner(data));

    // Fetch live status counts
    Promise.all([
      fetch(`${API_BASE_URL}/rooms?status=Pending`, { credentials: "include" }).then((r) => r.ok ? r.json() : []),
      fetch(`${API_BASE_URL}/rooms?status=Active`, { credentials: "include" }).then((r) => r.ok ? r.json() : []),
      fetch(`${API_BASE_URL}/rooms?status=Recovered`, { credentials: "include" }).then((r) => r.ok ? r.json() : []),
    ]).then(([pending, active, recovered]) => {
      setCounts({
        pending: pending.length || 0,
        active: active.length || 0,
        recovered: recovered.length || 0,
      });
    });
  }, []);

  return (
    <div className="max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Welcome back, {owner ? owner.display_name : "Owner"}!
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Monitor your permanent QR identity, review incoming contact requests, and coordinate returns.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <Link
          href="/dashboard/pending"
          className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-amber-300 transition-colors group block"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 group-hover:text-amber-600">
            Pending Requests
          </p>
          <p className="text-3xl font-black text-amber-500">{counts.pending}</p>
          <p className="text-xs text-slate-500 mt-2">Awaiting your approval →</p>
        </Link>

        <Link
          href="/dashboard/active"
          className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-emerald-300 transition-colors group block"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 group-hover:text-emerald-600">
            Active Conversations
          </p>
          <p className="text-3xl font-black text-emerald-600">{counts.active}</p>
          <p className="text-xs text-slate-500 mt-2">Two-way chat ongoing →</p>
        </Link>

        <Link
          href="/dashboard/recovered"
          className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-indigo-300 transition-colors group block"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 group-hover:text-indigo-600">
            Recovered Belongings
          </p>
          <p className="text-3xl font-black text-indigo-600">{counts.recovered}</p>
          <p className="text-xs text-slate-500 mt-2">Safely returned →</p>
        </Link>
      </div>

      {/* Quick Action Banner */}
      <div className="bg-emerald-600 text-white p-8 rounded-3xl shadow-md flex flex-col sm:flex-row justify-between items-center gap-6">
        <div>
          <h3 className="text-xl font-bold mb-2">Print Your Permanent QR Code</h3>
          <p className="text-emerald-100 text-sm max-w-xl">
            Attach this single QR code to your backpack, laptop, keys, and luggage. Any finder can scan it to message you directly without seeing your phone number.
          </p>
        </div>
        <a
          href="/dashboard/qr-code"
          className="px-6 py-3 bg-white text-emerald-800 font-bold rounded-xl shadow-sm hover:bg-emerald-50 transition-colors whitespace-nowrap"
        >
          View & Download QR
        </a>
      </div>
    </div>
  );
}
