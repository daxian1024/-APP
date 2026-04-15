const API_BASE = "http://127.0.0.1:5000/api";
let TOKEN = localStorage.getItem("token") || "";

function showToast(msg) {
  const el = document.getElementById("toast");
  el.innerText = msg;
  el.style.display = "block";
  setTimeout(() => (el.style.display = "none"), 1800);
}

function apiHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: TOKEN ? `Bearer ${TOKEN}` : "",
  };
}

function payloadOf(resp) {
  return resp?.data || {};
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

function toggleUserMenu() {
  document.getElementById("userMenu").classList.toggle("show");
}

function setActiveNav(panelId) {
  document.querySelectorAll(".nav-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.panel === panelId);
  });
}

function showPanel(panelId, btn) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add("active");
  if (btn) setActiveNav(panelId);
  document.getElementById("userMenu").classList.remove("show");
}

function fillDemoUser() {
  document.getElementById("account").value = "test01";
  document.getElementById("password").value = "123456";
}

function renderProfile(userText = "未登录") {
  const profileStatus = document.getElementById("profileStatus");
  if (profileStatus) profileStatus.innerText = userText;
}

function logout() {
  TOKEN = "";
  localStorage.removeItem("token");
  document.getElementById("loginInfo").innerText = "未登录";
  renderProfile("未登录");
  showToast("已退出登录");
  showPanel("authPanel");
  setActiveNav("authPanel");
}

async function registerUser() {
  const username = document.getElementById("reg_username").value.trim();
  const phone = document.getElementById("reg_phone").value.trim();
  const password = document.getElementById("reg_password").value;

  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, phone, password, role: "elderly" }),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "注册失败");

  document.getElementById("account").value = username;
  document.getElementById("password").value = password;
  showToast("注册成功，正在登录...");
  await login();
}

async function login() {
  const account = document.getElementById("account").value.trim();
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account, password }),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) {
    document.getElementById("loginInfo").innerText = data.message || "登录失败";
    return showToast(data.message || "登录失败");
  }

  const p = payloadOf(data);
  TOKEN = p.access_token;
  localStorage.setItem("token", TOKEN);

  const text = `已登录：${p.user.username} (${p.user.role})`;
  document.getElementById("loginInfo").innerText = text;
  renderProfile(text);
  showToast("登录成功");

  loadServices();
  loadAddresses();
  loadOrders();
  showPanel("servicesPanel");
  setActiveNav("servicesPanel");
}

async function loadServices() {
  const res = await fetch(`${API_BASE}/services`);
  const data = await res.json();
  const items = payloadOf(data).items || [];

  const el = document.getElementById("serviceList");
  el.innerHTML = "";
  items.forEach((it) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>#${it.id} ${it.name}</b></div><div class="muted">${it.description || ""}</div><div>￥${it.price} / ${it.duration_minutes}分钟</div>`;
    el.appendChild(li);
  });
}

async function loadPopularServices() {
  const res = await fetch(`${API_BASE}/services/popular`);
  const data = await res.json();
  const p = payloadOf(data);

  const el = document.getElementById("serviceList");
  el.innerHTML = "";
  (p.items || []).forEach((it) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>[热门] #${it.id} ${it.name}</b></div><div class="muted">来源：${p.source}</div><div>￥${it.price}</div>`;
    el.appendChild(li);
  });
}

async function addAddress() {
  if (!TOKEN) return showToast("请先登录");

  const payload = {
    contact_name: document.getElementById("contact_name").value.trim(),
    contact_phone: document.getElementById("contact_phone").value.trim(),
    province: document.getElementById("province").value.trim(),
    city: document.getElementById("city").value.trim(),
    district: document.getElementById("district").value.trim(),
    detail: document.getElementById("detail").value.trim(),
    is_default: true,
  };

  const res = await fetch(`${API_BASE}/addresses`, {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "地址新增失败");
  showToast("地址新增成功");
  loadAddresses();
}

async function loadAddresses() {
  if (!TOKEN) return;
  const res = await fetch(`${API_BASE}/addresses`, { headers: apiHeaders() });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return;

  const el = document.getElementById("addressList");
  el.innerHTML = "";
  (payloadOf(data).items || []).forEach((a) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>#${a.id} ${a.contact_name} ${a.contact_phone}</b></div><div class="muted">${a.province}${a.city}${a.district}${a.detail}</div>`;
    el.appendChild(li);
  });
}

async function updateAddress() {
  if (!TOKEN) return showToast("请先登录");
  const id = Number(document.getElementById("editAddressId").value);
  if (!id) return showToast("请输入待编辑地址ID");

  const payload = {
    contact_name: document.getElementById("contact_name").value.trim(),
    contact_phone: document.getElementById("contact_phone").value.trim(),
    province: document.getElementById("province").value.trim(),
    city: document.getElementById("city").value.trim(),
    district: document.getElementById("district").value.trim(),
    detail: document.getElementById("detail").value.trim(),
  };

  const res = await fetch(`${API_BASE}/addresses/${id}`, {
    method: "PATCH",
    headers: apiHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "地址编辑失败");
  showToast("地址编辑成功");
  loadAddresses();
}

async function deleteAddress() {
  if (!TOKEN) return showToast("请先登录");
  const id = Number(document.getElementById("deleteAddressId").value);
  if (!id) return showToast("请输入待删除地址ID");

  const res = await fetch(`${API_BASE}/addresses/${id}`, {
    method: "DELETE",
    headers: apiHeaders(),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "地址删除失败");
  showToast("地址删除成功");
  loadAddresses();
}

async function createOrder() {
  if (!TOKEN) return showToast("请先登录");

  const payload = {
    service_item_id: Number(document.getElementById("service_item_id").value),
    address_id: Number(document.getElementById("address_id").value),
    appointment_time: document.getElementById("appointment_time").value.trim(),
    note: document.getElementById("note").value.trim(),
  };

  const res = await fetch(`${API_BASE}/orders`, {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok || data.code !== 0) return showToast(data.message || "预约失败");
  const p = payloadOf(data);
  document.getElementById("timelineOrderId").value = p.order_id || "";
  document.getElementById("payOrderId").value = p.order_id || "";
  document.getElementById("reviewOrderId").value = p.order_id || "";
  document.getElementById("complaintOrderId").value = p.order_id || "";
  showToast(`预约成功：${p.order_no}`);
  loadOrders();
}

async function payOrder() {
  if (!TOKEN) return showToast("请先登录");
  const orderId = Number(document.getElementById("payOrderId").value);
  if (!orderId) return showToast("请输入订单ID");

  const res = await fetch(`${API_BASE}/orders/${orderId}/pay`, {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify({ method: "mock_alipay" }),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "支付失败");

  showToast(`支付成功：${payloadOf(data).transaction_no}`);
  loadOrders();
}

function statusTagClass(status) {
  if (status === "pending") return "pending";
  if (status === "accepted") return "accepted";
  if (status === "in_service") return "in_service";
  if (status === "completed") return "completed";
  return "pending";
}

async function loadOrders() {
  if (!TOKEN) return;

  const res = await fetch(`${API_BASE}/orders`, { headers: apiHeaders() });
  const data = await res.json();
  const items = payloadOf(data).items || [];

  const el = document.getElementById("orderList");
  el.innerHTML = "";
  items.forEach((it) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `
      <div><b>${it.order_no}</b></div>
      <div class="muted">${it.service_name} | ${it.appointment_time}</div>
      <div><span class="tag ${statusTagClass(it.status)}">${it.status}</span> <span class="muted">支付:${it.payment_status || "-"}</span></div>
    `;
    el.appendChild(li);
  });
}

async function loadTimeline() {
  if (!TOKEN) return showToast("请先登录");
  const orderId = Number(document.getElementById("timelineOrderId").value);
  if (!orderId) return showToast("请输入订单ID");

  const res = await fetch(`${API_BASE}/orders/${orderId}/timeline`, { headers: apiHeaders() });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "加载时间线失败");

  const el = document.getElementById("timelineList");
  el.innerHTML = "";
  (payloadOf(data).items || []).forEach((it) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>${it.from_status || "null"} → ${it.to_status}</b></div><div class="muted">${it.remark || ""} | ${it.created_at}</div>`;
    el.appendChild(li);
  });
}

async function createReview() {
  if (!TOKEN) return showToast("请先登录");
  const payload = {
    order_id: Number(document.getElementById("reviewOrderId").value),
    rating: Number(document.getElementById("reviewRating").value),
    comment: document.getElementById("reviewComment").value.trim(),
  };
  const res = await fetch(`${API_BASE}/feedback/reviews`, {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "评价失败");
  showToast("评价提交成功");
  loadMyReviews();
}

async function createComplaint() {
  if (!TOKEN) return showToast("请先登录");
  const payload = {
    order_id: Number(document.getElementById("complaintOrderId").value) || null,
    content: document.getElementById("complaintContent").value.trim(),
  };
  const res = await fetch(`${API_BASE}/feedback/complaints`, {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "投诉失败");
  showToast("投诉提交成功");
  loadMyComplaints();
}

async function loadMyReviews() {
  if (!TOKEN) return showToast("请先登录");
  const res = await fetch(`${API_BASE}/feedback/reviews`, { headers: apiHeaders() });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "加载评价失败");

  const el = document.getElementById("feedbackList");
  el.innerHTML = "";
  (payloadOf(data).items || []).forEach((r) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>评价#${r.id}</b> 订单:${r.order_id} 评分:${r.rating}</div><div class="muted">${r.comment || ""}</div>`;
    el.appendChild(li);
  });
}

async function loadMyComplaints() {
  if (!TOKEN) return showToast("请先登录");
  const res = await fetch(`${API_BASE}/feedback/complaints`, { headers: apiHeaders() });
  const data = await res.json();
  if (!res.ok || data.code !== 0) return showToast(data.message || "加载投诉失败");

  const el = document.getElementById("feedbackList");
  el.innerHTML = "";
  (payloadOf(data).items || []).forEach((c) => {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `<div><b>投诉#${c.id}</b> 订单:${c.order_id || "-"} 状态:${c.status}</div><div class="muted">${c.content}</div>`;
    el.appendChild(li);
  });
}

document.addEventListener("click", (e) => {
  const menu = document.getElementById("userMenu");
  if (!menu) return;
  if (!e.target.closest(".profile")) menu.classList.remove("show");
});

renderProfile(TOKEN ? "已登录" : "未登录");
loadServices();
