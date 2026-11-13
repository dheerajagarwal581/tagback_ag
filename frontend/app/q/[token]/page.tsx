"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { API_BASE_URL } from "@/lib/config";

export default function PublicQRScanPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [itemName, setItemName] = useState("");
  const [finderName, setFinderName] = useState("");
  const [initialMessage, setInitialMessage] = useState("");
  const [foundLocation, setFoundLocation] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successData, setSuccessData] = useState<any>(null);

  useEffect(() => {
    if (!token) return;

    fetch(`${API_BASE_URL}/qr/public/${token}`)
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "QR code inactive or not found.");
        }
        return res.json();
      })
      .then((data) => setProfile(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/contact/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          public_token: token,
          item_name: itemName,
          finder_display_name: finderName,
          initial_message: initialMessage,
          found_location: foundLocation || undefined,
          description: description || undefined,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to submit contact request.");
      }

      const data = await res.json();
      setSuccessData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-sm text-slate-500">
        Connecting to belonging owner...
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="p-8 bg-white border border-slate-200 rounded-3xl shadow-sm">
          <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-4 font-bold text-lg">
            ✕
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">QR Code Inactive</h2>
          <p className="text-sm text-slate-600 mb-6">{error}</p>
          <a
            href="/"
            className="inline-block py-2.5 px-6 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-xl transition-colors"
          >
            Go to Homepage
          </a>
        </div>
      </div>
    );
  }

  // Success view: Prompts finder to save recovery link before entering chat
  if (successData) {
    return (
      <div className="flex-1 flex items-center justify-center p-4 py-12">
        <div className="w-full max-w-lg bg-white border border-slate-200 rounded-3xl p-8 shadow-sm text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4 font-black text-xl">
            ✓
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Alert Sent to Owner!</h2>
          <p className="text-sm text-slate-600 mb-6">
            A temporary chat room has been created in <strong>Pending</strong> state. The owner has been notified.
          </p>

          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-left mb-6">
            <p className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-1">
              ⚠️ Save Your Recovery Link
            </p>
            <p className="text-xs text-amber-700 mb-3">
              Because you did not sign up, use this secret link to reopen this conversation if your browser tab closes:
            </p>
            <input
              type="text"
              readOnly
              value={successData.recovery_url}
              className="w-full p-2 text-xs bg-white border border-amber-300 rounded-lg font-mono text-slate-800 select-all mb-2"
            />
            <button
              onClick={() => navigator.clipboard.writeText(successData.recovery_url)}
              className="w-full py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              Copy Secret Recovery Link
            </button>
          </div>

          <button
            onClick={() => router.push(`/chat/${successData.room_id}`)}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-colors shadow-sm"
          >
            Enter Temporary Chat Room
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-10 max-w-xl mx-auto w-full">
      {/* Owner Greeting Card */}
      <div className="w-full bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm mb-6 text-center">
        <span className="inline-block px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold uppercase tracking-wider mb-3">
          Lost Belonging Tag
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          You Found {profile?.display_name}&apos;s Item!
        </h1>
        {profile?.public_bio && (
          <p className="text-sm text-slate-600 mt-2 bg-slate-50 p-3 rounded-xl border border-slate-100 italic">
            &ldquo;{profile.public_bio}&rdquo;
          </p>
        )}
        <p className="text-xs text-slate-500 mt-3">
          🔒 Contact the owner below. Neither your phone number nor the owner&apos;s will be shared.
        </p>
      </div>

      {/* Mobile-First Contact Form */}
      <div className="w-full bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900 mb-1">Send a Quick Alert</h2>
        <p className="text-xs text-slate-500 mb-5">
          Fill out this short form to open a temporary chat room.
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              What did you find? <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              placeholder="e.g. Black Backpack, Keychain, Laptop"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Your Temporary Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={finderName}
              onChange={(e) => setFinderName(e.target.value)}
              placeholder="e.g. Sam"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Where was it found? (Optional)
            </label>
            <input
              type="text"
              value={foundLocation}
              onChange={(e) => setFoundLocation(e.target.value)}
              placeholder="e.g. Student Center 2nd floor, Table 4"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Opening Message to Owner <span className="text-red-500">*</span>
            </label>
            <textarea
              required
              rows={3}
              value={initialMessage}
              onChange={(e) => setInitialMessage(e.target.value)}
              placeholder="Hi, I found your item! Where would you like to meet to return it?"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-colors shadow-sm disabled:opacity-50 text-sm"
          >
            {submitting ? "Sending Alert to Owner..." : "Send Alert & Start Chat"}
          </button>
        </form>
      </div>
    </div>
  );
}
