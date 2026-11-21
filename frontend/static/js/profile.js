// Rutas relativas: la app y la API comparten origen (sin localhost fijo)
const API_URL = "";

function authHeaders(extra = {}) {
    const token = localStorage.getItem("access_token");
    return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

document.addEventListener("DOMContentLoaded", async () => {
    const artistId = localStorage.getItem("artista_id");
    if (!artistId || artistId === "null" || artistId === "undefined" || !localStorage.getItem("access_token")) {
        console.warn("No hay sesión de artista activa. Redirigiendo al inicio...");
        window.location.href = "/";
        return;
    }

    const form = document.getElementById("profile-form");
    const nameInput = document.getElementById("profile-name");
    const redesInput = document.getElementById("profile-redes");
    const linksInput = document.getElementById("profile-links");
    const btnSkip = document.getElementById("btn-skip");
    const msgContainer = document.getElementById("profile-msg");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("profile-avatar-file");
    const dropZoneContent = document.getElementById("drop-zone-content");
    const previewContainer = document.getElementById("avatar-preview-container");
    const avatarPreview = document.getElementById("avatar-preview");
    const btnRemoveAvatar = document.getElementById("btn-remove-avatar");

    // Cargar datos actuales del perfil
    try {
        const response = await fetch(`${API_URL}/artists/${artistId}`);
        if (response.ok) {
            const data = await response.json();
            if (nameInput && data.name) nameInput.value = data.name;
            if (redesInput && data.redes) redesInput.value = data.redes;
            if (linksInput && data.links) linksInput.value = data.links;
            if (data.avatar) {
                showPreview(data.avatar);
            }
        }
    } catch (err) {
        console.error("Error de red al cargar el perfil:", err);
    }

    function showPreview(src) {
        if (avatarPreview && previewContainer && dropZoneContent) {
            avatarPreview.src = src;
            previewContainer.classList.remove("hidden");
            dropZoneContent.classList.add("hidden");
        }
    }

    function clearPreview() {
        if (avatarPreview && previewContainer && dropZoneContent && fileInput) {
            avatarPreview.src = "";
            fileInput.value = "";
            previewContainer.classList.add("hidden");
            dropZoneContent.classList.remove("hidden");
        }
    }

    if (btnRemoveAvatar) {
        btnRemoveAvatar.addEventListener("click", (e) => {
            e.stopPropagation();
            clearPreview();
        });
    }

    async function uploadAvatarFile(file) {
        if (!file || !file.type.startsWith("image/")) {
            alert("Por favor selecciona un archivo de imagen válido.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${API_URL}/artists/${artistId}/avatar`, {
                method: "PUT",
                headers: authHeaders(),
                body: formData
            });

            const data = await response.json();
            if (response.status === 401) { localStorage.clear(); window.location.href = "/"; return; }
            if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Error al subir la imagen.");

            showPreview(data.avatar);
        } catch (err) {
            alert(err.message);
        }
    }

    if (dropZone) {
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        ["dragleave", "dragend"].forEach((type) => {
            dropZone.addEventListener(type, () => {
                dropZone.classList.remove("dragover");
            });
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                uploadAvatarFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                uploadAvatarFile(e.target.files[0]);
            }
        });
    }

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (msgContainer) {
                msgContainer.textContent = "";
                msgContainer.className = "error-msg";
            }

            const profileData = {
                name: nameInput ? nameInput.value.trim() : "",
                redes: redesInput ? redesInput.value.trim() : "",
                links: linksInput ? linksInput.value.trim() : ""
            };

            try {
                const response = await fetch(`${API_URL}/artists/${artistId}`, {
                    method: "PUT",
                    headers: authHeaders({ "Content-Type": "application/json" }),
                    body: JSON.stringify(profileData)
                });

                const data = await response.json();
                if (response.status === 401) { localStorage.clear(); window.location.href = "/"; return; }
                if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Error al actualizar el perfil.");

                if (profileData.name) {
                    localStorage.setItem("artista_nombre", profileData.name);
                }

                if (msgContainer) {
                    msgContainer.textContent = "¡Perfil actualizado con éxito!";
                    msgContainer.className = "success-msg";
                }

                setTimeout(() => {
                    window.location.href = "/";
                }, 1200);

            } catch (err) {
                if (msgContainer) {
                    msgContainer.textContent = err.message;
                    msgContainer.className = "error-msg";
                }
            }
        });
    }

    if (btnSkip) {
        btnSkip.addEventListener("click", () => {
            window.location.href = "/";
        });
    }
});
