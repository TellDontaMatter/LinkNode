"use client";

import { useEffect, useState } from "react";
import {
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  User,
} from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiResult, setApiResult] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<number | null>(null);
  const [calling, setCalling] = useState(false);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return unsub;
  }, []);

  async function handleSignIn() {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      console.error("Sign-in error:", err);
    }
  }

  async function handleSignOut() {
    setApiResult(null);
    setApiStatus(null);
    await signOut(auth);
  }

  async function handleCallApi() {
    if (!user) return;
    setCalling(true);
    setApiResult(null);
    setApiStatus(null);
    try {
      const token = await user.getIdToken();
      const workerUrl = process.env.NEXT_PUBLIC_WORKER_URL;
      const res = await fetch(`${workerUrl}/api/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setApiStatus(res.status);
      const text = await res.text();
      try {
        setApiResult(JSON.stringify(JSON.parse(text), null, 2));
      } catch {
        setApiResult(text);
      }
    } catch (err) {
      setApiResult(String(err));
      setApiStatus(0);
    } finally {
      setCalling(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gray-950 text-white">
        <p className="text-gray-400">Loading…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold tracking-tight">SSE Agency</h1>

      {!user ? (
        <button
          onClick={handleSignIn}
          className="flex items-center gap-3 px-6 py-3 bg-white text-gray-900 font-semibold rounded-lg shadow hover:bg-gray-100 transition"
        >
          <svg className="w-5 h-5" viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.8 2.5 30.2 0 24 0 14.7 0 6.7 5.4 2.9 13.2l7.8 6.1C12.5 13.3 17.8 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17z"/>
            <path fill="#FBBC05" d="M10.7 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.7-4.7L2.4 13.2A23.9 23.9 0 0 0 0 24c0 3.8.9 7.4 2.5 10.6l8.2-5.9z"/>
            <path fill="#34A853" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7.5-5.8c-2 1.4-4.6 2.3-7.7 2.3-6.2 0-11.5-4.2-13.3-9.8l-8.1 6.2C6.6 42.5 14.7 48 24 48z"/>
          </svg>
          Sign in with Google
        </button>
      ) : (
        <div className="flex flex-col items-center gap-4 w-full max-w-md">
          <div className="flex items-center gap-3 bg-gray-800 rounded-lg px-4 py-3 w-full">
            {user.photoURL && (
              <img
                src={user.photoURL}
                alt="avatar"
                className="w-9 h-9 rounded-full"
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{user.displayName}</p>
              <p className="text-sm text-gray-400 truncate">{user.email}</p>
            </div>
            <button
              onClick={handleSignOut}
              className="text-sm text-gray-400 hover:text-white transition"
            >
              Sign out
            </button>
          </div>

          <button
            onClick={handleCallApi}
            disabled={calling}
            className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 disabled:cursor-wait font-semibold rounded-lg transition"
          >
            {calling ? "Calling…" : "Call API"}
          </button>

          {apiStatus !== null && (
            <div className="w-full bg-gray-800 rounded-lg p-4">
              <p className="text-sm mb-2">
                Status:{" "}
                <span
                  className={
                    apiStatus === 200
                      ? "text-green-400 font-bold"
                      : "text-red-400 font-bold"
                  }
                >
                  {apiStatus || "network error"}
                </span>
              </p>
              <pre className="text-xs text-gray-300 overflow-auto max-h-64 whitespace-pre-wrap break-all">
                {apiResult}
              </pre>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
