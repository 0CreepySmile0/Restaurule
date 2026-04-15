"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { viewAllMenu, createMenu, updateMenu, deleteMenu, logout } from "../../../lib/api";
import type { MenuItem } from "../../../lib/api";

export default function Page() {
  const router = useRouter();
  const [items, setItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<{ type: "create" | "edit" | "delete" | null; item?: MenuItem }>({ type: null });
  const [form, setForm] = useState({ item_name: "", description: "", price: 0 });
  const [actionLoading, setActionLoading] = useState<string | number | null>(null);
  const [logoutLoading, setLogoutLoading] = useState(false);

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await viewAllMenu();
      setItems(res || []);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (/401|403|Unauthorized|Forbidden/i.test(msg)) return router.push("/login");
      setError(msg);
    } finally { setLoading(false); }
  }

  async function handleCreate() {
    setActionLoading("create");
    try {
      await createMenu(form as any);
      setModal({ type: null });
      load();
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally { setActionLoading(null); }
  }

  async function handleEdit(item: MenuItem) {
    setActionLoading(item.id);
    try {
      await updateMenu(item.id, { item_name: form.item_name, description: form.description, price: form.price });
      setItems(prev => prev.map(it => (it.id === item.id ? { ...it, item_name: form.item_name, description: form.description, price: form.price } : it)));
      setModal({ type: null });
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally { setActionLoading(null); }
  }

  async function handleDelete(item: MenuItem) {
    setActionLoading(item.id);
    try {
      await deleteMenu(item.id);
      setItems(prev => prev.filter(it => it.id !== item.id));
      setModal({ type: null });
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally { setActionLoading(null); }
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
      router.push('/login');
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl">Manager — Menu</h1>
        <div className="flex gap-2">
          <button onClick={() => router.push('/manager/staff')} className="px-3 py-1 bg-indigo-600 text-white rounded">Manage Staff</button>
          <button onClick={() => { setModal({ type: "create" }); setForm({ item_name: "", description: "", price: 0 }); }} className="px-3 py-1 bg-blue-600 text-white rounded">Create</button>
          <button onClick={handleLogout} disabled={logoutLoading} className="px-3 py-1 bg-gray-600 text-white rounded">{logoutLoading ? "Logging out..." : "Logout"}</button>
        </div>
      </div>
      {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
      <div className="space-y-3">
        {items.map(item => (
          <div key={item.id} className="p-3 border rounded bg-white dark:bg-zinc-800 flex justify-between items-center">
            <div>
              <div className="font-medium">{item.item_name}</div>
              <div className="text-sm text-zinc-600">{item.description}</div>
            </div>
            <div className="flex gap-2 items-center">
              <div className="text-sm">{item.price}</div>
              <button onClick={() => { setModal({ type: "edit", item }); setForm({ item_name: item.item_name, description: item.description || "", price: item.price }); }} className="px-3 py-1 bg-yellow-500 rounded text-white">Edit</button>
              <button onClick={() => setModal({ type: "delete", item })} className="px-3 py-1 bg-red-600 rounded text-white">Delete</button>
            </div>
          </div>
        ))}
      </div>

      {modal.type === "create" && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Create Menu Item</h2>
            <input placeholder="Name" value={form.item_name} onChange={e => setForm({ ...form, item_name: e.target.value })} className="w-full p-2 border rounded mb-2" />
            <input placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} className="w-full p-2 border rounded mb-2" />
            <input type="number" placeholder="Price" value={form.price} onChange={e => setForm({ ...form, price: Number(e.target.value) })} className="w-full p-2 border rounded mb-2" />
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={handleCreate} disabled={actionLoading === "create"} className="px-3 py-1 bg-blue-600 text-white rounded">{actionLoading === "create" ? "Creating..." : "Create"}</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === "edit" && modal.item && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Edit Menu Item</h2>
            <input placeholder="Name" value={form.item_name} onChange={e => setForm({ ...form, item_name: e.target.value })} className="w-full p-2 border rounded mb-2" />
            <input placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} className="w-full p-2 border rounded mb-2" />
            <input type="number" placeholder="Price" value={form.price} onChange={e => setForm({ ...form, price: Number(e.target.value) })} className="w-full p-2 border rounded mb-2" />
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={() => handleEdit(modal.item!)} disabled={actionLoading === modal.item!.id} className="px-3 py-1 bg-blue-600 text-white rounded">{actionLoading === modal.item!.id ? "Saving..." : "Save"}</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === "delete" && modal.item && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Delete Menu Item</h2>
            <div>Are you sure you want to delete <strong>{modal.item.item_name}</strong>?</div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={() => handleDelete(modal.item!)} disabled={actionLoading === modal.item!.id} className="px-3 py-1 bg-red-600 text-white rounded">{actionLoading === modal.item!.id ? "Deleting..." : "Delete"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
