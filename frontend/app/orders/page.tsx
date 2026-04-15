"use client";

import React, { useEffect, useState } from "react";
import { getCustomerOrders, cancelOrder, Order } from "../../lib/api";
import { useRouter } from "next/navigation";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tableNumber, setTableNumber] = useState<number | null>(null);
  const [cancelingIds, setCancelingIds] = useState<number[]>([]);
  const [pendingCancelId, setPendingCancelId] = useState<number | null>(null);

  const router = useRouter();
  const appCurrency = process.env.NEXT_PUBLIC_APP_CURRENCY || "USD"

  useEffect(() => {
    try {
      const raw = localStorage.getItem("table_number");
      if (!raw) {
        setError("Table number not set. Please set your table from the menu.");
        setLoading(false);
        return;
      }
      const parsed = JSON.parse(raw);
      const num = parsed?.tableNumber ?? null;
      if (num == null) {
        setError("Table number not set. Please set your table from the menu.");
        setLoading(false);
        return;
      }
      setTableNumber(Number(num));
      getCustomerOrders(Number(num))
        .then((data) => {
          setOrders(Array.isArray(data) ? data : []);
        })
        .catch((err) => setError(err?.message || String(err) || "Failed to fetch orders"))
        .finally(() => setLoading(false));
    } catch (e) {
      setError("Failed to read table number");
      setLoading(false);
    }
  }, []);

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: appCurrency, minimumFractionDigits: 2 }).format(n);

  const total = orders.reduce((s, o) => s + (o.price ?? 0), 0);

  const handleCancel = async (orderId: number) => {
    if (cancelingIds.includes(orderId)) return;
    setError(null);
    setCancelingIds((s) => [...s, orderId]);
    try {
      await cancelOrder(orderId);
      // after successful cancel, refresh orders from server if we have table number
      if (tableNumber != null) {
        setLoading(true);
        try {
          const data = await getCustomerOrders(tableNumber);
          setOrders(Array.isArray(data) ? data : []);
        } catch (err: any) {
          setError(err?.message || String(err) || "Failed to refresh orders");
        } finally {
          setLoading(false);
        }
      } else {
        setOrders((prev) => prev.map((o) => (o.id === orderId ? { ...o, status: "cancelled" } : o)));
      }
    } catch (err: any) {
      setError(err?.message || String(err) || "Failed to cancel order");
    } finally {
      setCancelingIds((s) => s.filter((id) => id !== orderId));
    }
  };

  const handleConfirmCancel = async () => {
    if (pendingCancelId == null) return;
    await handleCancel(pendingCancelId);
    setPendingCancelId(null);
  };

  return (
    <div className="min-h-screen flex items-top justify-center bg-zinc-50 dark:bg-black font-sans p-6 pt-45">
      <div className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-[#0b0b0b] border-b border-zinc-100 dark:border-zinc-800">
        <div className="w-full max-w-3xl mx-auto p-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">My orders</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Table: {tableNumber ?? "—"}</p>
          </div>
          <div className="ml-auto">
            <button onClick={() => router.push("/")} className="px-3 py-2 bg-zinc-900 hover:bg-zinc-700 text-white rounded">Back to menu</button>
          </div>
        </div>
      </div>

      <div className="w-full max-w-3xl">
        {pendingCancelId != null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white dark:bg-zinc-900 p-6 rounded-lg shadow-lg w-full max-w-sm">
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-2">Confirm cancel</h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-4">Are you sure you want to cancel this order?</p>
              {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
              <div className="flex gap-2 justify-end">
                <button onClick={() => setPendingCancelId(null)} className="px-4 py-2 bg-transparent border rounded text-zinc-700 dark:text-zinc-300">Close</button>
                <button
                  onClick={handleConfirmCancel}
                  disabled={pendingCancelId == null || cancelingIds.includes(pendingCancelId)}
                  className="px-4 py-2 bg-red-600 text-white rounded disabled:opacity-50"
                >
                  {pendingCancelId != null && cancelingIds.includes(pendingCancelId) ? "Cancelling…" : "Confirm cancel"}
                </button>
              </div>
            </div>
          </div>
        )}
        <div className="bg-white dark:bg-[#0b0b0b] rounded-lg shadow-sm divide-y divide-zinc-100 dark:divide-zinc-800 overflow-hidden">

          <div className="p-6">
            <div className="sticky z-40 mb-4 flex justify-end">
              <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 bg-white/0 dark:bg-transparent px-2">Total: {loading ? "…" : fmt(total)}</div>
            </div>
            {loading ? (
              <div className="text-center text-zinc-600">Loading orders…</div>
            ) : error ? (
              <div className="text-center text-red-600">{error}</div>
            ) : orders.length === 0 ? (
              <div className="text-center text-zinc-600">You have no orders.</div>
            ) : (
              <div className="space-y-4">
                {orders.map((o) => (
                  <div key={o.id} className="p-4 border rounded bg-white dark:bg-zinc-900">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-medium text-zinc-900 dark:text-zinc-50">{o.item_name}</div>
                        <div className="text-sm text-zinc-500 dark:text-zinc-400">Qty: {o.quantity ?? 1} — {o.note ?? "No additional note"}</div>
                      </div>
                      <div className="text-right flex flex-col items-end gap-2">
                        <div className="font-semibold text-zinc-900 dark:text-zinc-50">{fmt(o.price)}</div>
                        <div className={`text-sm ${o.status === "served" ? "text-green-600" : o.status === "pending" ? "text-zinc-400" : "text-yellow-600"}`}>{o.status ?? "pending"}</div>
                        {String(o.status).toLowerCase() === "pending" && (
                          <button
                            onClick={() => setPendingCancelId(o.id)}
                            disabled={cancelingIds.includes(o.id)}
                            className="mt-1 px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded disabled:opacity-50"
                          >
                            {cancelingIds.includes(o.id) ? "Cancelling…" : "Cancel"}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
