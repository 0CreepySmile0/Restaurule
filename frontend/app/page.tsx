"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { getMenu } from "../lib/api";

type MenuItem = {
  id: number;
  item_name: string;
  description?: string | null;
  price: number;
};

export default function Home() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const appName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || "Restaurule";

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getMenu()
      .then((data) => {
        if (!mounted) return;
        setItems(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err?.message || String(err) || "Error fetching data");
        setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "THB", minimumFractionDigits: 2 }).format(n);

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black font-sans p-6">
      <div className="w-full max-w-3xl">
        <header className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            {appName}
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Our menu — freshly fetched from the kitchen</p>
        </header>

        <main className="bg-white dark:bg-[#0b0b0b] rounded-lg shadow-sm divide-y divide-zinc-100 dark:divide-zinc-800 overflow-hidden">
          {loading ? (
            <div className="p-6 text-center text-zinc-600">Loading menu…</div>
          ) : error ? (
            <div className="p-6 text-center text-red-600">{error}</div>
          ) : items.length === 0 ? (
            <div className="p-6 text-center text-zinc-600">No items available.</div>
          ) : (
            items.map((it) => (
              <div key={it.id} className="flex items-start justify-between p-6 hover:bg-zinc-50 dark:hover:bg-zinc-900">
                <div className="flex flex-col">
                  <div className="text-lg font-medium text-zinc-900 dark:text-zinc-50">{it.item_name}</div>
                  {it.description ? (
                    <div className="text-sm text-zinc-500 dark:text-zinc-400 mt-1 max-w-prose">{it.description}</div>
                  ) : (
                    <div className="text-sm text-zinc-400 dark:text-zinc-500 mt-1">No description</div>
                  )}
                </div>
                <div className="ml-4 text-right">
                  <div className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{fmt(it.price)}</div>
                </div>
              </div>
            ))
          )}
        </main>
      </div>
    </div>
  );
}
