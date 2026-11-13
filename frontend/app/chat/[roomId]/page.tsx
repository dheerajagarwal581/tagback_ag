"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { API_BASE_URL, WS_BASE_URL } from "@/lib/config";

export default function ChatRoomPage() {
  const params = useParams();
  const router = useRouter();
  const roomId = params.roomId as string;

  const [room, setRoom] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 1. Fetch Room Details
  useEffect(() => {
    if (!roomId) return;

    fetch(`${API_BASE_URL}/rooms/${roomId}`, {
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Room access denied.");
        }
        return res.json();
      })
      .then((data) => {
        setRoom(data);
        setMessages(data.messages || []);
      })
      .catch((err) => setErrorBanner(err.message))
      .finally(() => setLoading(false));
  }, [roomId]);

  // 2. Establish Real-Time WebSocket Connection
  useEffect(() => {
    if (!roomId) return;

    const wsUrl = `${WS_BASE_URL}/room/${roomId}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const frame = JSON.parse(event.data);
        if (frame.type === "NEW_MESSAGE") {
          setMessages((prev) => [...prev, frame.message]);
        } else if (frame.type === "ROOM_ACCEPTED") {
          setRoom((prev: any) => (prev ? { ...prev, status: "Active" } : prev));
        } else if (frame.type === "ROOM_TERMINATED") {
          setRoom((prev: any) => (prev ? { ...prev, status: "Closed" } : prev));
          setErrorBanner(frame.reason || "This conversation has been closed.");
        } else if (frame.type === "ERROR") {
          setErrorBanner(frame.detail);
          setTimeout(() => setErrorBanner(null), 5000);
        }
      } catch (e) {
        console.error("Malformed WebSocket message", e);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [roomId]);

  // Handle Send Message via WebSocket
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !socketRef.current) return;

    socketRef.current.send(
      JSON.stringify({
        type: "SEND_MESSAGE",
        content: inputMessage.trim(),
      })
    );
    setInputMessage("");
  };

  // Owner Action: Accept Request
  const handleAccept = async () => {
    const res = await fetch(`${API_BASE_URL}/rooms/${roomId}/accept`, {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) {
      setRoom((prev: any) => ({ ...prev, status: "Active" }));
    }
  };

  // Owner Action: Mark as Recovered
  const handleMarkRecovered = async () => {
    if (!confirm("Confirm that this belonging has been safely recovered? This will close the chat.")) {
      return;
    }
    const res = await fetch(`${API_BASE_URL}/rooms/${roomId}/recover`, {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) {
      setRoom((prev: any) => ({ ...prev, status: "Recovered" }));
      router.push("/dashboard/recovered");
    }
  };

  // Owner Action: Close Chat
  const handleCloseChat = async () => {
    if (!confirm("Are you sure you want to end this conversation?")) return;
    const res = await fetch(`${API_BASE_URL}/rooms/${roomId}/close`, {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) {
      setRoom((prev: any) => ({ ...prev, status: "Closed" }));
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-sm text-slate-500">
        Connecting to temporary room...
      </div>
    );
  }

  const isTerminal = room?.status === "Closed" || room?.status === "Recovered" || room?.status === "Rejected";

  return (
    <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-3 sm:p-6 h-[calc(100vh-64px)]">
      {/* Room Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-4 sm:p-5 shadow-sm mb-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span
              className={`w-3 h-3 rounded-full ${
                room?.status === "Active"
                  ? "bg-emerald-500 animate-pulse"
                  : room?.status === "Pending"
                  ? "bg-amber-500 animate-pulse"
                  : "bg-slate-400"
              }`}
            />
            <h1 className="font-extrabold text-slate-900 text-lg sm:text-xl">
              {room?.item_details?.item_name || "Belonging"}
            </h1>
            <span
              className={`px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                room?.status === "Active"
                  ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                  : room?.status === "Pending"
                  ? "bg-amber-50 text-amber-800 border border-amber-200"
                  : "bg-slate-100 text-slate-600 border border-slate-200"
              }`}
            >
              {room?.status}
            </span>
          </div>

          <p className="text-xs text-slate-500 mt-1">
            Finder: <strong className="text-slate-800">{room?.finder_display_name}</strong> • Owner:{" "}
            <strong className="text-slate-800">{room?.owner_display_name}</strong>
            {room?.item_details?.found_location && (
              <> • Location: <span>{room.item_details.found_location}</span></>
            )}
          </p>
        </div>

        {/* Action Controls for Owner */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          {room?.status === "Pending" && (
            <button
              onClick={handleAccept}
              className="flex-1 sm:flex-none px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
            >
              Accept Request to Reply
            </button>
          )}

          {room?.status === "Active" && (
            <>
              <button
                onClick={handleMarkRecovered}
                className="flex-1 sm:flex-none px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
              >
                Mark as Recovered
              </button>
              <button
                onClick={handleCloseChat}
                className="px-3.5 py-2 border border-slate-300 hover:bg-slate-100 text-slate-700 font-medium rounded-xl text-xs transition-colors"
              >
                End Chat
              </button>
            </>
          )}
        </div>
      </div>

      {/* Error / Warning Alert Banner */}
      {errorBanner && (
        <div className="mb-3 p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-xs flex justify-between items-center animate-fade-in">
          <span>⚠️ {errorBanner}</span>
          <button onClick={() => setErrorBanner(null)} className="font-bold text-rose-800 hover:underline">
            ✕
          </button>
        </div>
      )}

      {/* Real-Time Chat Message Feed */}
      <div className="flex-1 bg-white border border-slate-200 rounded-3xl p-4 sm:p-6 shadow-sm overflow-y-auto flex flex-col justify-between">
        <div className="space-y-4 mb-4">
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-600 text-center max-w-md mx-auto">
            🔒 <strong>Temporary Encrypted Channel:</strong> This conversation is isolated. Neither party&apos;s phone number or email is visible.
          </div>

          {messages.map((msg: any, idx: number) => {
            const isOwner = msg.sender_type === "owner";
            return (
              <div
                key={msg.id || idx}
                className={`flex flex-col ${isOwner ? "items-end" : "items-start"}`}
              >
                <span className="text-[10px] font-semibold text-slate-400 mb-1 px-1">
                  {msg.sender_display_name} ({msg.sender_type})
                </span>
                <div
                  className={`max-w-[85%] sm:max-w-md px-4 py-2.5 rounded-2xl text-sm shadow-sm ${
                    isOwner
                      ? "bg-emerald-600 text-white rounded-br-none"
                      : "bg-slate-100 text-slate-900 border border-slate-200 rounded-bl-none"
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                </div>
                <span className="text-[9px] text-slate-400 mt-1 px-1">
                  {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now"}
                </span>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input Bar */}
        {isTerminal ? (
          <div className="p-4 bg-slate-100 rounded-2xl text-center text-xs font-semibold text-slate-500">
            This conversation is {room?.status?.toLowerCase()}. Messaging is disabled and credentials have been revoked.
          </div>
        ) : (
          <form onSubmit={handleSendMessage} className="pt-3 border-t border-slate-100 flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                room?.status === "Pending"
                  ? "Finder can send follow-ups. Owner must click Accept to reply..."
                  : "Type your message..."
              }
              className="flex-1 px-4 py-3 rounded-2xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim()}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl text-sm transition-colors shadow-sm disabled:opacity-50"
            >
              Send
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
