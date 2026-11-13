"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { API_BASE_URL } from "@/lib/config";

export default function RecoveryPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    fetch(`${API_BASE_URL}/contact/recover/${token}`, {
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Recovery link invalid or conversation has ended.");
        }
        return res.json();
      })
      .then((data) => {
        // Successfully restored session! Redirect to chat room
        router.push(data.redirect_url);
      })
      .catch((err) => setError(err.message));
  }, [token, router]);

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="p-8 bg-white border border-slate-200 rounded-3xl shadow-sm">
          <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-4 font-bold text-lg">
            ✕
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Conversation Unavailable</h2>
          <p className="text-sm text-slate-600 mb-6">{error}</p>
          <a
            href="/"
            className="inline-block py-2.5 px-6 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-xl transition-colors"
          >
            Return to Homepage
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4" />
      <p className="text-sm font-semibold text-slate-700">Verifying recovery credentials...</p>
      <p className="text-xs text-slate-400 mt-1">Restoring your conversation with the owner</p>
    </div>
  );
}
