// Rutas relativas: la app y la API comparten origen (sin localhost fijo)
const API_URL = "";

function errorText(data, fallback) {
    if (typeof data?.detail === "string" && data.detail) return data.detail;
    if (Array.isArray(data?.detail)) {
        const msgs = data.detail.map((d) => d?.msg).filter(Boolean);
        if (msgs.length) return msgs.join(". ");
    }
    return fallback;
}

const btnLoginTab = document.getElementById("btn-login-tab");
const btnRegisterTab = document.getElementById("btn-register-tab");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

if (btnLoginTab && btnRegisterTab && loginForm && registerForm) {
    btnLoginTab.addEventListener("click", () => {
        btnLoginTab.classList.add("active");
        btnRegisterTab.classList.remove("active");
        loginForm.classList.remove("hidden");
        registerForm.classList.add("hidden");
    });
    btnRegisterTab.addEventListener("click", () => {
        btnRegisterTab.classList.add("active");
        btnLoginTab.classList.remove("active");
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
    });
}

const regPassword = document.getElementById("register-password");
const btnRegister = document.getElementById("btn-register");
const reqLength = document.getElementById("req-length");
const reqUpper = document.getElementById("req-upper");
const reqLower = document.getElementById("req-lower");
const reqNumber = document.getElementById("req-number");

if (regPassword && btnRegister) {
    regPassword.addEventListener("input", () => {
        const val = regPassword.value;
        const hasLength = val.length >= 8;
        const hasUpper = /[A-Z]/.test(val);
        const hasLower = /[a-z]/.test(val);
        const hasNumber = /\d/.test(val);

        if (reqLength) reqLength.className = hasLength ? "valid" : "invalid";
        if (reqUpper) reqUpper.className = hasUpper ? "valid" : "invalid";
        if (reqLower) reqLower.className = hasLower ? "valid" : "invalid";
        if (reqNumber) reqNumber.className = hasNumber ? "valid" : "invalid";

        if (hasLength && hasUpper && hasLower && hasNumber) {
            btnRegister.removeAttribute("disabled");
        } else {
            btnRegister.setAttribute("disabled", "true");
        }
    });
}

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("register-nombre").value;
        const email = document.getElementById("register-email").value;
        const password = regPassword ? regPassword.value : "";
        const errorMsg = document.getElementById("register-error");
        const successMsg = document.getElementById("register-success");

        if (errorMsg) errorMsg.textContent = "";
        if (successMsg) successMsg.textContent = "";

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(errorText(data, "Error en el registro"));
            }
            if (successMsg) successMsg.textContent = "¡Registro exitoso! Ya puedes iniciar sesión.";
            registerForm.reset();
            if (btnRegister) btnRegister.setAttribute("disabled", "true");
            if (reqLength) reqLength.className = "invalid";
            if (reqUpper) reqUpper.className = "invalid";
            if (reqLower) reqLower.className = "invalid";
            if (reqNumber) reqNumber.className = "invalid";
        } catch (err) {
            if (errorMsg) errorMsg.textContent = err.message;
        }
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        const errorMsg = document.getElementById("login-error");
        if (errorMsg) errorMsg.textContent = "";

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(errorText(data, "Credenciales incorrectas"));
            }
            if (!data.id) {
                throw new Error("No se pudo asociar un ID de artista válido.");
            }
            localStorage.setItem("artista_id", data.id);
            localStorage.setItem("artista_nombre", data.name);
            if (data.access_token) {
                localStorage.setItem("access_token", data.access_token);
            }
            window.location.href = "/dashboard";
        } catch (err) {
            if (errorMsg) errorMsg.textContent = err.message;
        }
    });
}
