"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "@/lib/config";

export default function PendingRequestsPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);

  const fetchPending = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/rooms?status=Pending`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setRequests(data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleAccept = async (roomId: string) => {
    setActionId(roomId);
    try {
      const res = await fetch(`${API_BASE_URL}/rooms/${roomId}/accept`, {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        router.push(`/chat/${roomId}`);
      }
    } finally {
      setActionId(null);
    }
  };

  const handleReject = async (roomId: string) => {
    if (!confirm("Are you sure you want to reject this request? The finder will be locked out.")) {
      return;
    }
    setActionId(roomId);
    try {
      const res = await fetch(`${API_BASE_URL}/rooms/${roomId}/reject`, {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        await fetchPending();
      }
    } finally {
      setActionId(null);
    }
  };

  if (loading) {
    return <div className="text-sm text-slate-500">Checking for pending requests...</div>;
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Pending Contact Requests
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Review incoming reports from finders who scanned your QR code. You must accept a request before replying.
        </p>
      </div>

      {requests.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center shadow-sm">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3 font-bold text-lg">
            ✓
          </div>
          <h3 className="font-bold text-slate-800 text-lg mb-1">No Pending Requests</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            When someone scans your physical QR code and submits an item report, it will show up here immediately.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((req) => (
            <div
              key={req.room_id}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
                  <h3 className="font-bold text-slate-900 text-lg">{req.item_name}</h3>
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 text-xs font-semibold">
                    Pending Acceptance
                  </span>
                </div>

                <p className="text-sm text-slate-600">
                  Reported by <strong className="text-slate-800">{req.finder_display_name}</strong>
                  {req.found_location && (
                    <> at <span className="text-slate-700 font-medium">{req.found_location}</span></>
                  )}
                </p>

                <div className="bg-slate-50 border border-slate-100 p-3 rounded-xl text-xs text-slate-700 italic">
                  &ldquo;{req.initial_message}&rdquo;
                </div>

                <p className="text-xs text-slate-400">
                  Received on {new Date(req.created_at).toLocaleString()}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex sm:flex-col gap-2.5 w-full md:w-auto">
                <button
                  onClick={() => handleAccept(req.room_id)}
                  disabled={actionId === req.room_id}
                  className="flex-1 md:flex-none px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-sm transition-colors shadow-sm disabled:opacity-50 whitespace-nowrap"
                >
                  {actionId === req.room_id ? "Accepting..." : "Accept & Open Chat"}
                </button>
                <button
                  onClick={() => handleReject(req.room_id)}
                  disabled={actionId === req.room_id}
                  className="px-4 py-2 border border-slate-200 text-slate-600 hover:bg-slate-100 font-medium rounded-xl text-xs transition-colors disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
