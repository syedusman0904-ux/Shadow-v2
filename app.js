let accessToken = null;
let currentUser = null;
let registerMode = true;

const $ = (id) => document.getElementById(id);

function setMode(register) {
  registerMode = register;
  $("auth-title").textContent = register ? "Welcome to SHADOW" : "Welcome back";
  $("auth-subtitle").textContent = register ? "Create your private account." : "Login to your account.";
  $("display-name-wrap").style.display = register ? "grid" : "none";
  $("display-name").required = register;
  $("auth-button").textContent = register ? "Create account" : "Login";
  $("toggle-auth").textContent = register
    ? "Already have an account? Login"
    : "Need an account? Register";
  $("password").autocomplete = register ? "new-password" : "current-password";
  $("error").textContent = "";
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function showApp(user) {
  currentUser = user;
  $("auth-screen").classList.add("hidden");
  $("app-screen").classList.remove("hidden");

  $("welcome").textContent = `Hello, ${user.display_name}`;
  $("profile-name").textContent = user.display_name;
  $("profile-username").textContent = `@${user.username}`;
  $("profile-id").textContent = `User ID: ${user.id}`;
  $("avatar").textContent = (user.display_name || "S")[0].toUpperCase();
}

function showAuth() {
  accessToken = null;
  currentUser = null;
  $("app-screen").classList.add("hidden");
  $("auth-screen").classList.remove("hidden");
}

$("toggle-auth").addEventListener("click", () => setMode(!registerMode));

$("auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("error").textContent = "";

  const payload = {
    username: $("username").value.trim(),
    password: $("password").value,
  };
  if (registerMode) payload.display_name = $("display-name").value.trim();

  try {
    const data = await api(registerMode ? "/auth/register" : "/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    accessToken = data.access_token;
    showApp(data.user);
  } catch (error) {
    $("error").textContent = error.message;
  }
});

$("logout").addEventListener("click", async () => {
  try { await api("/auth/logout", { method: "POST" }); } catch (_) {}
  showAuth();
  $("auth-form").reset();
});

async function restoreSession() {
  try {
    const data = await api("/auth/refresh", { method: "POST" });
    accessToken = data.access_token;
    showApp(data.user);
  } catch (_) {
    setMode(true);
  }
}

restoreSession();
