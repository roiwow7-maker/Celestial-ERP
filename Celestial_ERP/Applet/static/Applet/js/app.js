document.querySelectorAll("[data-collapse-panel]").forEach((panel) => {
    const button = panel.querySelector("[data-collapse-toggle]");
    const body = panel.querySelector("[data-collapse-body]");
    if (!button || !body) {
        return;
    }

    const setExpanded = (expanded) => {
        body.classList.toggle("d-none", !expanded);
        button.setAttribute("aria-expanded", expanded ? "true" : "false");
        button.textContent = expanded ? "Cerrar" : "Abrir";
    };

    button.addEventListener("click", () => {
        setExpanded(button.getAttribute("aria-expanded") !== "true");
    });
});

const themeButtons = document.querySelectorAll("[data-theme-toggle]");

const applyThemeLabel = () => {
    const activeTheme = document.documentElement.dataset.erpTheme || "light";
    themeButtons.forEach((button) => {
        button.textContent = activeTheme === "dark" ? "Oscuro" : "Claro";
        button.setAttribute(
            "aria-label",
            activeTheme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro",
        );
    });
};

themeButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const activeTheme = document.documentElement.dataset.erpTheme || "light";
        const nextTheme = activeTheme === "dark" ? "light" : "dark";
        document.documentElement.dataset.erpTheme = nextTheme;
        document.documentElement.dataset.bsTheme = nextTheme;
        localStorage.setItem("celestial-erp-theme", nextTheme);
        applyThemeLabel();
    });
});

applyThemeLabel();
