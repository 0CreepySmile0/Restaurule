"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { chefViewOrders, cookOrder, finishOrder, chefCancel, logout } from "../../lib/api";
import type { Order } from "../../lib/api";

export default function Page() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [confirmCancelId, setConfirmCancelId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logoutLoading, setLogoutLoading] = useState(false);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await chefViewOrders();
      setOrders(res || []);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (/401|403|Unauthorized|Forbidden/i.test(msg)) return router.push("/login");
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleCook(id: number) {
    setActionLoading(id);
    try {
      await cookOrder(id);
      setOrders(prev => prev.map(o => (o.id === id ? { ...o, status: "cooking" } : o)));
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setActionLoading(null);
    }
  }

  async function handleDone(id: number) {
    setActionLoading(id);
    try {
      await finishOrder(id);
      // remove the order from the list when finished
      setOrders(prev => prev.filter(o => o.id !== id));
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCancel(id: number) {
    setActionLoading(id);
    try {
      await chefCancel(id);
      setOrders(prev => prev.filter(o => o.id !== id));
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setActionLoading(null);
    }
  }

  function confirmCancel(id: number) {
    setConfirmCancelId(id);
  }

  async function doConfirmCancel() {
    if (confirmCancelId == null) return;
    setActionLoading(confirmCancelId);
    try {
      await chefCancel(confirmCancelId);
      setOrders(prev => prev.filter(o => o.id !== confirmCancelId));
      setConfirmCancelId(null);
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setActionLoading(null);
    }
  }

  if (loading) return <div className="p-6">Loading...</div>;

  async function handleLogout() {
    setLogoutLoading(true);
    try {
      await logout();
    } catch (err) {
      // ignore errors, still redirect
    } finally {
      setLogoutLoading(false);
      router.push("/login");
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl">Chef Orders</h1>
        <button onClick={handleLogout} disabled={logoutLoading} className="px-3 py-1 bg-gray-600 text-white rounded">{logoutLoading ? "Logging out..." : "Logout"}</button>
      </div>
      {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
      <div className="space-y-4">
        {orders.length === 0 && <div>No orders</div>}
        {orders.map(order => (
          <div key={order.id} className="p-4 border rounded bg-white dark:bg-zinc-800">
            <div className="flex justify-between items-start">
              <div>
                <div className="font-medium">Table #{order.table_number} — {order.item_name}</div>
                <div className="text-sm text-zinc-600 dark:text-zinc-300">Qty: {order.quantity ?? 1} • {order.note ?? ""}</div>
                <div className="text-sm">Price: {order.price}</div>
              </div>
              <div className="text-sm">Status: <strong>{order.status}</strong></div>
            </div>
            <div className="mt-3 flex gap-2">
              {order.status === "pending" && (
                <button onClick={() => handleCook(order.id)} disabled={actionLoading === order.id} className="px-3 py-1 bg-yellow-500 rounded text-white">
                  {actionLoading === order.id ? "..." : "Cook"}
                </button>
              )}

              {order.status === "cooking" && (
                <button onClick={() => handleDone(order.id)} disabled={actionLoading === order.id} className="px-3 py-1 bg-green-600 rounded text-white">
                  {actionLoading === order.id ? "..." : "Done"}
                </button>
              )}

              <button onClick={() => confirmCancel(order.id)} disabled={actionLoading === order.id} className="px-3 py-1 bg-red-600 rounded text-white">
                {actionLoading === order.id ? "..." : "Cancel"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {confirmCancelId != null && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Cancel Order</h2>
            <div>Are you sure you want to cancel this order?</div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setConfirmCancelId(null)} className="px-3 py-1 rounded">No</button>
              <button onClick={doConfirmCancel} disabled={actionLoading === confirmCancelId} className="px-3 py-1 bg-red-600 text-white rounded">{actionLoading === confirmCancelId ? "Cancelling..." : "Yes, cancel"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
