"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "@/lib/config";

export default function ActiveChatsPage() {
  const router = useRouter();
  const [rooms, setRooms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/rooms?status=Active`, {
      credentials: "include",
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setRooms(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-sm text-slate-500">Loading active conversations...</div>;
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Active Conversations
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Coordinate meeting locations and safe handovers with finders in real time.
        </p>
      </div>

      {rooms.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center shadow-sm">
          <h3 className="font-bold text-slate-800 text-lg mb-1">No Active Conversations</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            Once you accept a pending request from a finder, it will appear here for live chat.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {rooms.map((room) => (
            <div
              key={room.room_id}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <h3 className="font-bold text-slate-900 text-lg">{room.item_name}</h3>
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 text-xs font-semibold">
                    Live Chat Active
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-1">
                  Chatting with <strong className="text-slate-800">{room.finder_display_name}</strong>
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Started on {new Date(room.created_at).toLocaleDateString()}
                </p>
              </div>

              <button
                onClick={() => router.push(`/chat/${room.room_id}`)}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-sm transition-colors shadow-sm whitespace-nowrap"
              >
                Open Live Chat
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
