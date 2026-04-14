"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { viewStaffs, createStaff, updateStaffRole, deleteStaff, logout } from "../../../lib/api";
import type { User } from "../../../lib/api";

const ROLES = ["chef", "waiter", "waitress", "manager"];

export default function Page() {
  const router = useRouter();
  const [staff, setStaff] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<{ type: "create" | "update" | "delete" | null; staff?: User }>(
    { type: null }
  );
  const [form, setForm] = useState({ username: "", password: "", first: "", last: "", role: ROLES[0] });
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [logoutLoading, setLogoutLoading] = useState(false);

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await viewStaffs();
      setStaff(res || []);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (/401|403|Unauthorized|Forbidden/i.test(msg)) return router.push("/login");
      setError(msg);
    } finally { setLoading(false); }
  }

  async function handleCreate() {
    setActionLoading("create");
    try {
      await createStaff(form as any);
      setModal({ type: null });
      load();
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally { setActionLoading(null); }
  }

  async function handleUpdateRole(st: User, newRole: string) {
    setActionLoading(st.id);
    try {
      await updateStaffRole(st.id, newRole);
      setStaff(prev => prev.map(s => (s.id === st.id ? { ...s, role: newRole } : s)));
      setModal({ type: null });
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally { setActionLoading(null); }
  }

  async function handleDelete(st: User) {
    setActionLoading(st.id);
    try {
      await deleteStaff(st.id);
      setStaff(prev => prev.filter(s => s.id !== st.id));
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
        <h1 className="text-2xl">Manager — Staff</h1>
        <div className="flex gap-2">
          <button onClick={() => { setModal({ type: "create" }); setForm({ username: "", password: "", first: "", last: "", role: ROLES[0] }); }} className="px-3 py-1 bg-blue-600 text-white rounded">Create</button>
          <button onClick={handleLogout} disabled={logoutLoading} className="px-3 py-1 bg-gray-600 text-white rounded">{logoutLoading ? "Logging out..." : "Logout"}</button>
        </div>
      </div>
      {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
      <div className="space-y-3">
        {staff.map(s => (
          <div key={s.id} className="p-3 border rounded bg-white dark:bg-zinc-800 flex justify-between items-center">
            <div>
              <div className="font-medium">{s.username} — {s.first} {s.last}</div>
              <div className="text-sm">Role: {s.role}</div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setModal({ type: "update", staff: s })} className="px-3 py-1 bg-yellow-500 rounded text-white">Change role</button>
              <button onClick={() => setModal({ type: "delete", staff: s })} className="px-3 py-1 bg-red-600 rounded text-white">Delete</button>
            </div>
          </div>
        ))}
      </div>

      {/* Modals */}
      {modal.type === "create" && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Create Staff</h2>
            <div className="space-y-2">
              <input placeholder="username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} className="w-full p-2 border rounded" />
              <input placeholder="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} className="w-full p-2 border rounded" />
              <input placeholder="first" value={form.first} onChange={e => setForm({ ...form, first: e.target.value })} className="w-full p-2 border rounded" />
              <input placeholder="last" value={form.last} onChange={e => setForm({ ...form, last: e.target.value })} className="w-full p-2 border rounded" />
              <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="w-full p-2 border rounded">
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={handleCreate} disabled={actionLoading === "create"} className="px-3 py-1 bg-blue-600 text-white rounded">{actionLoading === "create" ? "Creating..." : "Create"}</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === "update" && modal.staff && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Update Role — {modal.staff.username}</h2>
            <select defaultValue={modal.staff.role} onChange={e => setModal({ ...modal, staff: { ...modal.staff!, role: e.target.value } })} className="w-full p-2 border rounded">
              {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={() => handleUpdateRole(modal.staff!, (modal.staff as any).role)} disabled={!!actionLoading} className="px-3 py-1 bg-blue-600 text-white rounded">{actionLoading === modal.staff!.id ? "Updating..." : "Confirm"}</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === "delete" && modal.staff && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-zinc-800 p-6 rounded w-full max-w-md">
            <h2 className="text-lg mb-3">Delete Staff</h2>
            <div>Are you sure you want to delete <strong>{modal.staff.username}</strong>?</div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setModal({ type: null })} className="px-3 py-1 rounded">Cancel</button>
              <button onClick={() => handleDelete(modal.staff!)} disabled={!!actionLoading} className="px-3 py-1 bg-red-600 text-white rounded">{actionLoading === modal.staff!.id ? "Deleting..." : "Delete"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
