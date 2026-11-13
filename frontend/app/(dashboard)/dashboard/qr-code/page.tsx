"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/config";

export default function QRCodePage() {
  const [qrData, setQrData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchQR = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/qr/my-code`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setQrData(data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQR();
  }, []);

  const handleCopy = () => {
    if (qrData?.qr_url) {
      navigator.clipboard.writeText(qrData.qr_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerate = async () => {
    if (
      !confirm(
        "Are you sure you want to regenerate your QR code? Old printed QR codes will be permanently deactivated for new scans."
      )
    ) {
      return;
    }

    setRegenerating(true);
    try {
      const res = await fetch(`${API_BASE_URL}/qr/regenerate`, {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        await fetchQR();
      }
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return <div className="text-sm text-slate-500">Loading your QR identity...</div>;
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Your Permanent QR Code
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          This single QR code connects all your personal belongings to your account.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm flex flex-col md:flex-row items-center gap-10">
        {/* QR Code Preview */}
        <div className="flex flex-col items-center">
          <div className="p-4 bg-white border border-slate-300 rounded-2xl shadow-inner mb-4">
            {/* Direct image stream from FastAPI backend */}
            <img
              src={`${API_BASE_URL}/qr/download`}
              alt="Permanent QR Code"
              className="w-56 h-56 object-contain"
            />
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Active Digital Identity
          </span>
        </div>

        {/* Action Details */}
        <div className="flex-1 space-y-5 text-left w-full">
          <div>
            <h3 className="font-bold text-slate-900 text-lg mb-1">Print & Label Belongings</h3>
            <p className="text-sm text-slate-600">
              Download this high-resolution QR image. Print multiple sticker copies and stick them on your:
            </p>
            <ul className="text-xs text-slate-500 mt-2 list-disc list-inside space-y-1">
              <li>Backpack & Laptop Bag</li>
              <li>Laptop case & Tablet</li>
              <li>Keychain & Luggage tags</li>
            </ul>
          </div>

          <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Encoded Scan URL</p>
            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={qrData?.qr_url || ""}
                className="w-full bg-transparent text-xs text-slate-800 font-mono focus:outline-none"
              />
              <button
                onClick={handleCopy}
                className="px-3 py-1 bg-white border border-slate-300 text-xs font-medium text-slate-700 rounded-lg hover:bg-slate-100 transition-colors whitespace-nowrap shadow-sm"
              >
                {copied ? "Copied!" : "Copy URL"}
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <a
              href={`${API_BASE_URL}/qr/download`}
              download="permanent_qr.png"
              className="flex-1 text-center py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-xl shadow-sm transition-colors"
            >
              Download PNG
            </a>
            <button
              onClick={handleRegenerate}
              disabled={regenerating}
              className="py-2.5 px-4 border border-rose-200 text-rose-600 hover:bg-rose-50 text-sm font-medium rounded-xl transition-colors disabled:opacity-50"
            >
              {regenerating ? "Regenerating..." : "Regenerate Code"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
