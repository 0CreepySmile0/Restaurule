"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { waiterViewOrders, serveOrder, checkout, logout } from "../../lib/api";
import type { Order } from "../../lib/api";

export default function Page() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logoutLoading, setLogoutLoading] = useState(false);

  const appCurrency = process.env.NEXT_PUBLIC_APP_CURRENCY || "USD"
  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: appCurrency, minimumFractionDigits: 2 }).format(n);

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await waiterViewOrders();
      setOrders(res || []);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (/401|403|Unauthorized|Forbidden/i.test(msg)) return router.push("/login");
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function groupByTable(items: Order[]) {
    return items.reduce<Record<number, Order[]>>((acc, o) => {
      const t = Number(o.table_number) || 0;
      if (!acc[t]) acc[t] = [];
      acc[t].push(o);
      return acc;
    }, {});
  }

  async function handleServe(id: number) {
    setActionLoading(id);
    try {
      await serveOrder(id);
      setOrders(prev => prev.map(o => (o.id === id ? { ...o, status: "served" } : o)));
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCheckout(tableNumber: number) {
    setCheckoutLoading(tableNumber);
    try {
      await checkout(tableNumber);
      setOrders(prev => prev.filter(o => Number(o.table_number) !== tableNumber));
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setCheckoutLoading(null);
    }
  }

  if (loading) return <div className="p-6">Loading...</div>;

  async function handleLogout() {
    setLogoutLoading(true);
    try {
      await logout();
    } catch (err) {
      // ignore
    } finally {
      setLogoutLoading(false);
      router.push("/login");
    }
  }

  const grouped = groupByTable(orders);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl">Waiter — Tables</h1>
        <button onClick={handleLogout} disabled={logoutLoading} className="px-3 py-1 bg-gray-600 text-white rounded">{logoutLoading ? "Logging out..." : "Logout"}</button>
      </div>
      {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
      <div className="space-y-6">
        {Object.keys(grouped).length === 0 && <div>No active tables</div>}
        {Object.entries(grouped).map(([table, items]) => {
          const tnum = Number(table);
          const total = items.reduce((s, it) => s + ((it.quantity ?? 1) * (it.price ?? 0)), 0);
          const allServed = items.every(it => it.status === "served");
          return (
            <div key={table} className="p-4 border rounded bg-white dark:bg-zinc-800">
              <div className="flex justify-between items-center">
                <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 bg-white/0 dark:bg-transparent">Table #{tnum}</div>
                <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 bg-white/0 dark:bg-transparent">Total: {fmt(total)}</div>
              </div>
              <div className="mt-3 space-y-2">
                {items.map(it => (
                  <div key={it.id} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{it.item_name} <span className="text-sm">x{it.quantity ?? 1}</span></div>
                      <div className={`text-sm ${it.status === "served" ? "text-green-600" : it.status === "pending" ? "text-zinc-400" : "text-yellow-600"}`}>{it.status}</div>
                      <div className="text-sm text-zinc-600">{it.note ?? ""}</div>
                    </div>
                    <div className="flex gap-2">
                      {it.status === "serving" && (
                        <button onClick={() => handleServe(it.id)} disabled={actionLoading === it.id} className="px-3 py-1 bg-green-600 text-white rounded">
                          {actionLoading === it.id ? "..." : "Serve"}
                        </button>
                      )}
                      <div className="text-sm">{fmt(it.price)}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-end">
                <button onClick={() => handleCheckout(tnum)} disabled={!allServed || checkoutLoading === tnum} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-60">
                  {checkoutLoading === tnum ? "Processing..." : "Checkout"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
