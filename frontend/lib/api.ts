type MenuItem = {
  id: number;
  item_name: string;
  description?: string | null;
  price: number;
};

type Order = any;
type User = any;

const BASE = (process.env.NEXT_PUBLIC_BASE_API_URL || "").replace(/\/$/, "");

async function request(path: string, options: RequestInit = {}) {
  const url = `${BASE}${path}`;
  const opts: RequestInit = {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  };

  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText || String(res.status));
  }

  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return null;
}

// Customer
export async function getMenu(): Promise<MenuItem[]> {
  return request(`/customer`) as Promise<MenuItem[]>;
}

export async function getCustomerOrders(tableNumber: number): Promise<Order[]> {
  return request(`/customer/orders/${tableNumber}`) as Promise<Order[]>;
}

export async function postCustomerOrder(tableNumber: number, itemId: number, note?: string, quantity = 1) {
  return request(`/customer/order/${tableNumber}`, {
    method: "POST",
    body: JSON.stringify({ item_id: itemId, note, quantity }),
  });
}

export async function cancelOrder(orderId: number) {
  return request(`/customer/cancel/${orderId}`, { method: "PATCH" });
}

export async function checkout(tableNumber: number) {
  return request(`/customer/checkout/${tableNumber}`);
}

// Auth
export async function register(data: { username: string; password: string; first: string; last: string; role: string }) {
  return request(`/register`, { method: "POST", body: JSON.stringify(data) });
}

export async function login(data: { username: string; password: string }) {
  return request(`/login`, { method: "POST", body: JSON.stringify(data) });
}

export async function logout() {
  return request(`/logout`, { method: "POST" });
}

// Chef
export async function chefViewOrders(): Promise<Order[]> {
  return request(`/chef`) as Promise<Order[]>;
}

export async function cookOrder(orderId: number) {
  return request(`/chef/cook/${orderId}`, { method: "PATCH" });
}

export async function chefCancel(orderId: number) {
  return request(`/chef/cancel/${orderId}`, { method: "PATCH" });
}

export async function finishOrder(orderId: number) {
  return request(`/chef/finish/${orderId}`, { method: "PATCH" });
}

// Waiter
export async function waiterViewOrders(): Promise<Order[]> {
  return request(`/waiter`) as Promise<Order[]>;
}

export async function serveOrder(orderId: number) {
  return request(`/waiter/serve/${orderId}`, { method: "PATCH" });
}

// Manager: staff
export async function createStaff(data: { username: string; password: string; first: string; last: string; role: string }) {
  return request(`/manager/staff`, { method: "POST", body: JSON.stringify(data) });
}

export async function viewStaffs(): Promise<User[]> {
  return request(`/manager/staff`) as Promise<User[]>;
}

export async function updateStaffRole(staffId: string, role: string) {
  return request(`/manager/staff/${staffId}/${role}`, { method: "PATCH" });
}

export async function deleteStaff(staffId: string) {
  return request(`/manager/staff/${staffId}`, { method: "DELETE" });
}

// Manager: menu
export async function createMenu(data: { item_name: string; description?: string; price: number }) {
  return request(`/manager/menu`, { method: "POST", body: JSON.stringify(data) });
}

export async function viewAllMenu(): Promise<MenuItem[]> {
  return request(`/manager/menu`) as Promise<MenuItem[]>;
}

export async function updateMenu(itemId: number, data: { item_name: string; description?: string; price: number }) {
  return request(`/manager/menu/${itemId}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function deleteMenu(itemId: number) {
  return request(`/manager/menu/${itemId}`, { method: "DELETE" });
}

const api = {
  // customer
  getMenu,
  getCustomerOrders,
  postCustomerOrder,
  cancelOrder,
  checkout,
  // auth
  register,
  login,
  logout,
  // chef
  chefViewOrders,
  cookOrder,
  chefCancel,
  finishOrder,
  // waiter
  waiterViewOrders,
  serveOrder,
  // manager staff
  createStaff,
  viewStaffs,
  updateStaffRole,
  deleteStaff,
  // manager menu
  createMenu,
  viewAllMenu,
  updateMenu,
  deleteMenu,
};

export type { MenuItem, Order, User };
export default api;
