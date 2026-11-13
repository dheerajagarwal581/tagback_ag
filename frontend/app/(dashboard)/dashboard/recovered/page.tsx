"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/config";

export default function RecoveredItemsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/rooms?status=Recovered`, {
      credentials: "include",
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setItems(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-sm text-slate-500">Loading recovered history...</div>;
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Recovered Belongings
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Historical record of all items successfully returned through the platform.
        </p>
      </div>

      {items.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center shadow-sm">
          <h3 className="font-bold text-slate-800 text-lg mb-1">No Recovered Items Yet</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            When you complete a return and click &ldquo;Mark as Recovered&rdquo; in chat, it will be archived here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div
              key={item.room_id}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex justify-between items-center"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-600" />
                  <h3 className="font-bold text-slate-900 text-lg">{item.item_name}</h3>
                  <span className="px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold">
                    Safely Recovered
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Returned by {item.finder_display_name} • Resolved on{" "}
                  {new Date(item.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
