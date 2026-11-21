// Rutas relativas: la app y la API comparten origen (sin localhost fijo)
const API_URL = "";

let currentPage = 1;
const limit = 6;

document.addEventListener("DOMContentLoaded", () => {
    checkSession();
    loadPublications();
    setupEventListeners();
});

function checkSession() {
    const artistName = localStorage.getItem("artista_nombre");
    const token = localStorage.getItem("access_token");
    const userDisplay = document.getElementById("user-display-name");

    if (token && artistName && userDisplay) {
        userDisplay.textContent = `Hola, ${artistName}`;
    }
}

function setupEventListeners() {
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            localStorage.clear();
            window.location.href = "/";
        });
    }

    const btnFilter = document.getElementById("btn-apply-filters");
    if (btnFilter) {
        btnFilter.addEventListener("click", () => {
            currentPage = 1;
            loadPublications();
        });
    }

    const btnPrev = document.getElementById("btn-prev-page");
    const btnNext = document.getElementById("btn-next-page");

    if (btnPrev) {
        btnPrev.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                loadPublications();
            }
        });
    }

    if (btnNext) {
        btnNext.addEventListener("click", () => {
            currentPage++;
            loadPublications();
        });
    }

    const btnOpenUpload = document.getElementById("btn-open-upload-modal");
    const uploadModal = document.getElementById("upload-modal");
    const btnCloseUpload = document.getElementById("btn-close-upload-modal");

    if (btnOpenUpload && uploadModal) {
        btnOpenUpload.addEventListener("click", () => {
            uploadModal.classList.remove("hidden");
        });
    }

    if (btnCloseUpload && uploadModal) {
        btnCloseUpload.addEventListener("click", () => {
            uploadModal.classList.add("hidden");
        });
    }

    const uploadForm = document.getElementById("upload-project-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const token = localStorage.getItem("access_token");
            const errorMsg = document.getElementById("upload-error");
            if (errorMsg) errorMsg.textContent = "";

            if (!token) {
                alert("No hay sesión de artista activa.");
                window.location.href = "/";
                return;
            }

            const formData = new FormData();
            formData.append("title", document.getElementById("post-title").value.trim());
            formData.append("publication_type", document.getElementById("post-type").value.trim());
            formData.append("genre_programming", document.getElementById("post-genre").value.trim());
            formData.append("description", document.getElementById("post-description").value.trim());

            const coverFile = document.getElementById("post-cover").files[0];
            if (coverFile) {
                formData.append("cover", coverFile);
            }

            const galleryFiles = document.getElementById("post-gallery").files;
            for (let i = 0; i < galleryFiles.length; i++) {
                formData.append("gallery", galleryFiles[i]);
            }

            try {
                const response = await fetch(`${API_URL}/posts/`, {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` },
                    body: formData
                });
                const data = await response.json();
                if (response.status === 401) {
                    localStorage.clear();
                    window.location.href = "/";
                    return;
                }
                if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Error al crear la publicación.");

                uploadForm.reset();
                uploadModal.classList.add("hidden");
                currentPage = 1;
                loadPublications();
            } catch (err) {
                if (errorMsg) errorMsg.textContent = err.message;
            }
        });
    }

    const btnCloseModal = document.getElementById("btn-close-modal");
    const modal = document.getElementById("detail-modal");
    if (btnCloseModal && modal) {
        btnCloseModal.addEventListener("click", () => {
            modal.classList.add("hidden");
        });
    }
}

async function loadPublications() {
    const grid = document.getElementById("posts-grid");
    const pageIndicator = document.getElementById("page-indicator");
    const btnPrev = document.getElementById("btn-prev-page");
    const btnNext = document.getElementById("btn-next-page");

    if (!grid) return;

    const search = document.getElementById("filter-search").value.trim();
    const type = document.getElementById("filter-type").value.trim();
    const genre = document.getElementById("filter-genre").value.trim();

    const skip = (currentPage - 1) * limit;

    let url = `${API_URL}/posts/?skip=${skip}&limit=${limit}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (type) url += `&publication_type=${encodeURIComponent(type)}`;
    if (genre) url += `&genre_programming=${encodeURIComponent(genre)}`;

    grid.innerHTML = "<p style='color: #94a3b8; grid-column: 1/-1;'>Cargando proyectos...</p>";

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Error al obtener las publicaciones.");

        const data = await response.json();
        grid.innerHTML = "";

        if (data.length === 0) {
            grid.innerHTML = "<p style='color: #94a3b8; grid-column: 1/-1;'>No se encontraron proyectos.</p>";
            if (btnNext) btnNext.disabled = true;
        } else {
            data.forEach(item => {
                const card = createCardElement(item);
                grid.appendChild(card);
            });
            if (btnNext) btnNext.disabled = data.length < limit;
        }

        if (pageIndicator) pageIndicator.textContent = `Página ${currentPage}`;
        if (btnPrev) btnPrev.disabled = currentPage === 1;

    } catch (err) {
        const errorP = document.createElement("p");
        errorP.style.cssText = "color: #ef4444; grid-column: 1/-1;";
        errorP.textContent = err.message;
        grid.replaceChildren(errorP);
    }
}

function createCardElement(item) {
    const card = document.createElement("div");
    card.className = "form-container";
    card.style.cssText = "padding: 20px; cursor: pointer; display: flex; flex-direction: column; justify-content: space-between;";

    const title = item.title || "Sin título";
    const desc = item.description ? (item.description.length > 90 ? item.description.substring(0, 90) + "..." : item.description) : "";
    const typeGenre = `${item.publication_type || ""} ${item.genre_programming ? "• " + item.genre_programming : ""}`;

    // Todo el contenido entra por textContent: evita XSS con datos del usuario
    const body = document.createElement("div");

    if (item.cover_image) {
        const wrap = document.createElement("div");
        wrap.style.cssText = "width: 100%; height: 140px; margin-bottom: 12px; border-radius: 6px; overflow: hidden; background-color: #0f172a;";
        const img = document.createElement("img");
        img.src = item.cover_image;
        img.alt = "Portada";
        img.style.cssText = "width: 100%; height: 100%; object-fit: cover;";
        wrap.appendChild(img);
        body.appendChild(wrap);
    }

    const meta = document.createElement("span");
    meta.style.cssText = "font-size: 11px; color: #38bdf8; font-weight: 600; text-transform: uppercase;";
    meta.textContent = typeGenre;

    const h3 = document.createElement("h3");
    h3.style.cssText = "margin: 6px 0; font-size: 18px; color: #f8fafc;";
    h3.textContent = title;

    const p = document.createElement("p");
    p.style.cssText = "font-size: 13px; color: #94a3b8; line-height: 1.4; margin-bottom: 0;";
    p.textContent = desc;

    body.append(meta, h3, p);

    const button = document.createElement("button");
    button.className = "btn";
    button.type = "button";
    button.style.cssText = "margin-top: 15px; font-size: 12px; padding: 8px;";
    button.textContent = "Ver Detalle";

    card.append(body, button);
    card.addEventListener("click", () => openDetailModal(item));
    return card;
}

function openDetailModal(item) {
    const modal = document.getElementById("detail-modal");
    const title = document.getElementById("modal-title");
    const typeGenre = document.getElementById("modal-type-genre");
    const desc = document.getElementById("modal-description");
    const coverContainer = document.getElementById("modal-cover-container");
    const coverImg = document.getElementById("modal-cover");
    const galleryContainer = document.getElementById("modal-gallery-container");
    const galleryGrid = document.getElementById("modal-gallery");
    const tagsContainer = document.getElementById("modal-tags");

    if (modal && title && typeGenre && desc) {
        title.textContent = item.title;
        typeGenre.textContent = `${item.publication_type || ''} ${item.genre_programming ? '• ' + item.genre_programming : ''}`;
        desc.textContent = item.description || "Sin descripción proporcionada.";

        if (item.cover_image && coverContainer && coverImg) {
            coverImg.src = item.cover_image;
            coverContainer.style.display = "block";
        } else if (coverContainer) {
            coverContainer.style.display = "none";
        }

        if (galleryContainer && galleryGrid) {
            galleryGrid.innerHTML = "";
            if (item.gallery_images) {
                try {
                    const galleryUrls = JSON.parse(item.gallery_images);
                    if (galleryUrls && galleryUrls.length > 0) {
                        galleryUrls.forEach(url => {
                            const img = document.createElement("img");
                            img.src = url;
                            img.alt = "Imagen de galería";
                            img.style.width = "100%";
                            img.style.height = "90px";
                            img.style.objectFit = "cover";
                            img.style.borderRadius = "4px";
                            img.style.border = "1px solid #334155";
                            galleryGrid.appendChild(img);
                        });
                        galleryContainer.style.display = "block";
                    } else {
                        galleryContainer.style.display = "none";
                    }
                } catch (e) {
                    galleryContainer.style.display = "none";
                }
            } else {
                galleryContainer.style.display = "none";
            }
        }

        tagsContainer.innerHTML = "";
        if (item.tags && item.tags.length > 0) {
            item.tags.forEach(tag => {
                const tagBadge = document.createElement("span");
                tagBadge.style.backgroundColor = "#0f172a";
                tagBadge.style.border = "1px solid #334155";
                tagBadge.style.color = "#38bdf8";
                tagBadge.style.padding = "4px 8px";
                tagBadge.style.borderRadius = "4px";
                tagBadge.style.fontSize = "12px";
                tagBadge.textContent = `#${tag.name}`;
                tagsContainer.appendChild(tagBadge);
            });
        }

        modal.classList.remove("hidden");
    }
}
