export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col justify-center items-center px-4 py-16 text-center max-w-4xl mx-auto">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold uppercase tracking-wider mb-6">
        Privacy-First Lost & Found
      </div>
      <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight mb-6">
        Recover your lost items <br className="hidden sm:inline" />
        <span className="text-emerald-600">without sharing your phone number.</span>
      </h1>
      <p className="text-lg sm:text-xl text-slate-600 mb-10 max-w-2xl">
        One permanent QR code protects all your belongings. When someone finds your lost item, they scan the code to start a temporary, isolated chat with you—without registration or app installs.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center w-full max-w-md mb-16">
        <a
          href="/register"
          className="w-full sm:w-auto px-8 py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-md transition-all text-center"
        >
          Create Permanent QR
        </a>
        <a
          href="/login"
          className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-800 font-semibold rounded-xl border border-slate-300 shadow-sm transition-all text-center"
        >
          Open Owner Dashboard
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left w-full border-t border-slate-200 pt-12">
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold mb-4">
            1
          </div>
          <h3 className="font-bold text-slate-900 mb-2">One Code for Everything</h3>
          <p className="text-sm text-slate-600">
            Attach duplicates of your permanent QR code to your keys, laptop, backpack, and wallet.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold mb-4">
            2
          </div>
          <h3 className="font-bold text-slate-900 mb-2">Account-Free Finder Scan</h3>
          <p className="text-sm text-slate-600">
            Finders simply point their camera, see your public greeting, and send a message. Zero friction.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold mb-4">
            3
          </div>
          <h3 className="font-bold text-slate-900 mb-2">Temporary Isolated Chat</h3>
          <p className="text-sm text-slate-600">
            Communicate in real-time. Once the item is safely returned, close the room and revoke all access.
          </p>
        </div>
      </div>
    </div>
  );
}
