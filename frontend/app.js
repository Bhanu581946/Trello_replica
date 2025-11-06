// ====== Simple FastAPI Auth Frontend ======
const qs = (sel) => document.querySelector(sel);

// === Constants ===
const BASE_URL = "http://127.0.0.1:8000";  // 👈 Fixed base URL
const TOKEN_KEY = "fastapi_access_token";

// === Token helpers ===
function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  qs("#accessToken").value = token;
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  qs("#accessToken").value = "";
}

// === Toast (popup message) ===
function toast(msg, type = "success") {
  const el = qs("#toast");
  el.textContent = msg;
  el.className = `toast show ${type}`;
  setTimeout(() => (el.className = "toast"), 2200);
}

// === API Calls ===
async function apiSignup({ username, email, password }) {
  const res = await fetch(`${BASE_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  return data;
}

async function apiLogin({ username, password }) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Login failed");
  return data; // { access_token, token_type }
}

async function apiMe() {
  const token = getToken();
  if (!token) throw new Error("No token. Please login first.");
  const res = await fetch(`${BASE_URL}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Failed to fetch /me");
  return data;
}

// ====== Wire up UI ======
window.addEventListener("DOMContentLoaded", () => {
  // Restore stored token
  const storedToken = getToken();
  if (storedToken) qs("#accessToken").value = storedToken;

  // Signup form
  qs("#signupForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = qs("#su_username").value.trim();
    const email = qs("#su_email").value.trim();
    const password = qs("#su_password").value;
    try {
      const user = await apiSignup({ username, email, password });
      toast(`Signed up as ${user.username}`);
    } catch (err) {
      toast(err.message || "Signup error", "error");
    }
  });

  // Login form
  qs("#loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = qs("#li_username").value.trim();
    const password = qs("#li_password").value;
    try {
      const { access_token, token_type } = await apiLogin({ username, password });
      setToken(access_token);
      toast(`Logged in (${token_type})`);
    } catch (err) {
      toast(err.message || "Login error", "error");
    }
  });

  // Copy token
  qs("#copyToken").addEventListener("click", async () => {
    const token = qs("#accessToken").value.trim();
    if (!token) return toast("No token to copy", "error");
    try {
      await navigator.clipboard.writeText(token);
      toast("Token copied");
    } catch {
      toast("Copy failed", "error");
    }
  });

  // Clear token (logout)
  qs("#clearToken").addEventListener("click", () => {
    clearToken();
    toast("Logged out");
  });

  // Fetch /me
  qs("#btnMe").addEventListener("click", async () => {
    const out = qs("#meOutput");
    out.textContent = "Loading...";
    try {
      const me = await apiMe();
      out.textContent = JSON.stringify(me, null, 2);
      toast("Fetched /me");
    } catch (err) {
      out.textContent = `Error: ${err.message || err}`;
      toast(err.message || "Failed to fetch /me", "error");
    }
  });
});
