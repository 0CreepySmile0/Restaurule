"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../lib/api";

export default function Page() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username || !password) return setError("Please fill username and password");
    setLoading(true);
    setError(null);
    try {
      const res = await login({ username, password }) as any;
      const role = res?.role;
      if (role) router.push(`/${role}`);
      else setError(res?.message || "Unexpected response from server");
    } catch (err: any) {
      setError("Incorrect username or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-900">
      <form onSubmit={handleSubmit} className="w-full max-w-md p-6 rounded bg-white dark:bg-zinc-800 shadow">
        <h1 className="text-2xl mb-4">Login</h1>
        {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
        <label className="block mb-2">
          <div className="text-sm">Username</div>
          <input value={username} onChange={e => setUsername(e.target.value)} className="mt-1 w-full p-2 border rounded" />
        </label>
        <label className="block mb-4">
          <div className="text-sm">Password</div>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 w-full p-2 border rounded" />
        </label>
        <div className="flex items-center justify-between">
          <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-60">
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </div>
      </form>
    </div>
  );
}
