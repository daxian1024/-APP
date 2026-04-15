const API = "http://127.0.0.1:5000/api";
let TOKEN = localStorage.getItem("admin_token") || "";
let ROLE = localStorage.getItem("admin_role") || "";
let PERMS = JSON.parse(localStorage.getItem("admin_perms") || "[]");
const SIGN_SECRET = "sign-secret-change-me";

function fillAdmin() {
  document.getElementById("account").value = "admin";
  document.getElementById("password").value = "123456";
}
function fillNurse() {
  document.getElementById("account").value = "nurse01";
  document.getElementById("password").value = "123456";
}

function hasPerm(p) {
  return PERMS.includes(p);
}

function renderPermissionUI() {
  document.getElementById("assignCard").classList.toggle("hidden", !hasPerm("admin:order:assign"));
  document.getElementById("serviceCard").classList.toggle("hidden", !hasPerm("admin:service:crud"));
  document.getElementById("statusCard").classList.toggle(
    "hidden",
    !(hasPerm("admin:order:update_status_any") || hasPerm("admin:order:update_status_assigned"))
  );
}

function h() {
  return {
    "Content-Type": "application/json",
    Authorization: TOKEN ? `Bearer ${TOKEN}` : "",
  };
}

async function hmacSha256Hex(secret, text) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(text));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function stableStringify(obj) {
  const keys = Object.keys(obj || {}).sort();
  const out = {};
  keys.forEach((k) => {
    out[k] = obj[k];
  });
  return JSON.stringify(out);
}

async function signHeaders(method, path, body) {
  const ts = String(Math.floor(Date.now() / 1000));
  const canonical = `${method}\n${path}\n${ts}\n${stableStringify(body || {})}`;
  const signature = await hmacSha256Hex(SIGN_SECRET, canonical);
  document.getElementById("sigTs").value = ts;
  return { "X-Timestamp": ts, "X-Signature": signature };
}

async function loginAdmin() {
  const account = document.getElementById("account").value.trim();
  const password = document.getElementById("password").value;
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account, password }),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return alert(data.message || "登录失败");

  TOKEN = data.data.access_token;
  ROLE = data.data.user.role;
  PERMS = data.data.permissions || [];
  localStorage.setItem("admin_token", TOKEN);
  localStorage.setItem("admin_role", ROLE);
  localStorage.setItem("admin_perms", JSON.stringify(PERMS));

  document.getElementById("who").innerText = `已登录: ${data.data.user.username} (${ROLE})`;
  renderPermissionUI();
}

async function loadAdminOrders() {
  const res = await fetch(`${API}/admin/orders`, { headers: h() });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return alert(data.message || "加载失败");

  const el = document.getElementById("orders");
  el.innerHTML = "";
  (data.data.items || []).forEach((o) => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `<b>${o.order_no}</b><div class='muted'>状态:${o.status} | 护士:${o.assigned_nurse_id || "-"} | 支付:${o.payment_status}</div>`;
    el.appendChild(div);
  });
}

async function assignNurse() {
  const orderId = Number(document.getElementById("assignOrderId").value);
  const nurseId = Number(document.getElementById("assignNurseId").value);
  const body = { nurse_id: nurseId };
  const path = `/api/admin/orders/${orderId}/assign`;
  const sh = await signHeaders("PATCH", path, body);

  const res = await fetch(`${API}/admin/orders/${orderId}/assign`, {
    method: "PATCH",
    headers: { ...h(), ...sh },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  alert(data.message || "ok");
}

async function updateStatus() {
  const orderId = Number(document.getElementById("statusOrderId").value);
  const status = document.getElementById("nextStatus").value;
  const body = { status };
  const path = `/api/admin/orders/${orderId}/status`;
  const sh = await signHeaders("PATCH", path, body);

  const res = await fetch(`${API}/admin/orders/${orderId}/status`, {
    method: "PATCH",
    headers: { ...h(), ...sh },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  alert(data.message || "ok");
}

async function createService() {
  const body = {
    name: document.getElementById("svcName").value.trim(),
    price: Number(document.getElementById("svcPrice").value),
    duration_minutes: Number(document.getElementById("svcDuration").value || 30),
    description: document.getElementById("svcDesc").value.trim(),
  };
  const path = "/api/services";
  const sh = await signHeaders("POST", path, body);
  const res = await fetch(`${API}/services`, { method: "POST", headers: { ...h(), ...sh }, body: JSON.stringify(body) });
  const data = await res.json();
  alert(data.message || "ok");
}

async function updateService() {
  const id = Number(document.getElementById("svcId").value);
  const body = {
    name: document.getElementById("svcName").value.trim(),
    price: Number(document.getElementById("svcPrice").value),
    duration_minutes: Number(document.getElementById("svcDuration").value || 30),
    description: document.getElementById("svcDesc").value.trim(),
  };
  const path = `/api/services/${id}`;
  const sh = await signHeaders("PATCH", path, body);
  const res = await fetch(`${API}/services/${id}`, { method: "PATCH", headers: { ...h(), ...sh }, body: JSON.stringify(body) });
  const data = await res.json();
  alert(data.message || "ok");
}

async function deleteService() {
  const id = Number(document.getElementById("svcId").value);
  const body = {};
  const path = `/api/services/${id}`;
  const sh = await signHeaders("DELETE", path, body);
  const res = await fetch(`${API}/services/${id}`, { method: "DELETE", headers: { ...h(), ...sh } });
  const data = await res.json();
  alert(data.message || "ok");
}

renderPermissionUI();
