"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMenu, postCustomerOrder } from "../lib/api";

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
  const [tableNumber, setTableNumber] = useState<number | null>(null);
  const [showTablePrompt, setShowTablePrompt] = useState(false);
  const [tableInput, setTableInput] = useState("");
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [pendingItem, setPendingItem] = useState<MenuItem | null>(null);
  const [orderNote, setOrderNote] = useState("");
  const [orderQuantity, setOrderQuantity] = useState<number>(1);
  const [ordering, setOrdering] = useState(false);
  const [orderError, setOrderError] = useState<string | null>(null);
  const [orderSuccess, setOrderSuccess] = useState<string | null>(null);
  const [pendingRedirect, setPendingRedirect] = useState<string | null>(null);

  const router = useRouter();
  const STORAGE_KEY = "table_number";

  const appName = process.env.NEXT_PUBLIC_APP_NAME || "Restaurule";
  const appQuote = process.env.NEXT_PUBLIC_APP_QUOTE || "Our menu our rule — freshly from the kitchen"

  useEffect(() => {
    // Table number persistence: check localStorage for existing table and expiry
    const TTL = 2 * 60 * 60 * 1000; // 2 hours in ms

    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        const ts = parsed?.ts ?? 0;
        const num = parsed?.tableNumber ?? null;
        const age = Date.now() - ts;
        if (num != null && age < TTL) {
          setTableNumber(Number(num));
          // schedule expiry
          setTimeout(() => {
            localStorage.removeItem(STORAGE_KEY);
            setTableNumber(null);
          }, TTL - age);
        } else {
          localStorage.removeItem(STORAGE_KEY);
        }
      }
    } catch (e) {}

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

  const saveTableNumber = (n: number) => {
    const TTL = 2 * 60 * 60 * 1000; // 2 hours
    const payload = { tableNumber: n, ts: Date.now() };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch (e) {
      // ignore storage errors
    }
    setTableNumber(n);
    setShowTablePrompt(false);
    if (pendingItem) {
      setSelectedItem(pendingItem);
      setOrderNote("");
      setOrderQuantity(1);
      setOrderError(null);
      setPendingItem(null);
    }
    if (pendingRedirect) {
      const dest = pendingRedirect;
      setPendingRedirect(null);
      router.push(dest);
    }
    setTimeout(() => {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {}
      setTableNumber(null);
      setShowTablePrompt(true);
    }, TTL);
  };

  const handleOrdersClick = (e?: React.MouseEvent) => {
    e?.preventDefault();
    try {
      const raw = localStorage.getItem("table_number");
      if (!raw) {
        setPendingRedirect("/orders");
        setShowTablePrompt(true);
        return;
      }
      const parsed = JSON.parse(raw);
      const num = parsed?.tableNumber ?? null;
      if (num == null) {
        setPendingRedirect("/orders");
        setShowTablePrompt(true);
        return;
      }
      router.push("/orders");
    } catch (err) {
      setPendingRedirect("/orders");
      setShowTablePrompt(true);
    }
  };

  const handleTableSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const v = Number(tableInput);
    if (!Number.isInteger(v) || v <= 0) return;
    saveTableNumber(v);
  };

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "THB", minimumFractionDigits: 2 }).format(n);

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black font-sans p-6 pt-20">
      <div className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-[#0b0b0b] border-b border-zinc-100 dark:border-zinc-800">
        <div className="w-full max-w-3xl mx-auto p-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">{appName}</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">{appQuote}</p>
          </div>
          <div className="ml-auto">
            <button type="button" onClick={handleOrdersClick} className="px-3 py-2 bg-zinc-900 hover:bg-zinc-700 text-white rounded">My orders</button>
          </div>
        </div>
      </div>
      <div className="w-full max-w-3xl">
        {showTablePrompt && (
          <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50">
            <form onSubmit={handleTableSubmit} className="bg-white dark:bg-zinc-900 p-6 rounded-lg shadow-lg w-full max-w-sm">
              <h2 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">Welcome — what's your table number?</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-4">We'll remember this table for 2 hours.</p>
              <input
                type="number"
                min={1}
                value={tableInput}
                onChange={(e) => setTableInput(e.target.value)}
                className="w-full p-2 border rounded mb-4 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50"
                placeholder="Table number"
                required
              />
              <div className="flex gap-2 justify-end">
                <button type="submit" className="px-4 py-2 bg-zinc-900 hover:bg-zinc-700 text-white rounded">Confirm</button>
              </div>
            </form>
          </div>
        )}
        {selectedItem && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                if (!tableNumber) return setShowTablePrompt(true);
                setOrdering(true);
                setOrderError(null);
                try {
                  await postCustomerOrder(tableNumber, selectedItem.id, orderNote || undefined, orderQuantity);
                  setOrderSuccess("Order placed");
                  setSelectedItem(null);
                } catch (err: any) {
                  setOrderError(err?.message || String(err) || "Order failed");
                } finally {
                  setOrdering(false);
                }
              }}
              className="bg-white dark:bg-zinc-900 p-6 rounded-lg shadow-lg w-full max-w-md"
            >
              <h2 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">Order: {selectedItem.item_name}</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-4">Add a note (optional) and quantity then confirm your order.</p>
              <textarea
                value={orderNote}
                onChange={(e) => setOrderNote(e.target.value)}
                placeholder="Add note (e.g., no onions)"
                className="w-full p-2 border rounded mb-3 h-20 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50"
              />
              <div className="flex items-center gap-3 mb-4">
                <label className="text-sm text-zinc-700 dark:text-zinc-300">Quantity</label>
                <input
                  type="number"
                  min={1}
                  value={orderQuantity}
                  onChange={(e) => setOrderQuantity(Math.max(1, Number(e.target.value || 1)))}
                  className="w-20 p-2 border rounded bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50"
                />
                <div className="ml-auto text-sm text-zinc-700 dark:text-zinc-300">Price: {fmt(selectedItem.price)}</div>
              </div>
              {orderError && <div className="text-sm text-red-600 mb-2">{orderError}</div>}
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setSelectedItem(null)} className="px-4 py-2 bg-transparent border rounded text-zinc-700 dark:text-zinc-300">Cancel</button>
                <button type="submit" disabled={ordering} className="px-4 py-2 bg-zinc-900 hover:bg-zinc-700 text-white rounded">{ordering ? "Ordering…" : "Order"}</button>
              </div>
            </form>
          </div>
        )}
        <header className="mb-6 pt-2">
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
              <div
                key={it.id}
                role="button"
                tabIndex={0}
                onClick={() => {
                  const num = localStorage.getItem(STORAGE_KEY)
                  if (num != null) {
                    setSelectedItem(it);
                    setOrderNote("");
                    setOrderQuantity(1);
                    setOrderError(null);
                  } else {
                    setPendingItem(it);
                    setShowTablePrompt(true);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    const num = localStorage.getItem(STORAGE_KEY)
                    if (num != null) {
                      setSelectedItem(it);
                      setOrderNote("");
                      setOrderQuantity(1);
                      setOrderError(null);
                    } else {
                      setPendingItem(it);
                      setShowTablePrompt(true);
                    }
                  }
                }}
                className="flex items-start justify-between p-6 hover:bg-zinc-50 dark:hover:bg-zinc-900 cursor-pointer"
              >
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
