"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const links = [
  ["/", "Inicio"],
  ["/nosotros", "Nosotros"],
  ["/servicios", "Servicios"],
  ["/contacto", "Contacto"],
  ["/trabaja-con-nosotros", "Trabaja con nosotros"],
] as const;

export function PublicNavbar() {
  const [open, setOpen] = useState(false);
  const nav = useRef<HTMLElement>(null);
  const menuButton = useRef<HTMLButtonElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    let theme = document.documentElement.dataset.theme;
    try { theme = localStorage.getItem("celestial-theme") ?? theme; } catch { /* Storage may be disabled. */ }
    document.documentElement.dataset.theme = theme === "dark" ? "dark" : "light";
  }, []);

  useEffect(() => {
    if (!open) return;
    function closeOutside(event: PointerEvent) {
      if (!nav.current?.contains(event.target as Node)) setOpen(false);
    }
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") { setOpen(false); menuButton.current?.focus(); }
    }
    document.addEventListener("pointerdown", closeOutside);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  function toggleTheme() {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("celestial-theme", next); } catch { /* The theme still works without storage. */ }
  }

  return (
    <nav ref={nav} className="floating-nav" aria-label="Navegación principal">
      <Link className="public-brand" href="/" onClick={() => setOpen(false)}>
        <span className="brand-mark" aria-hidden="true">C</span><strong>Celestial ERP</strong>
      </Link>
      <div id="public-navigation" className={`nav-links${open ? " is-open" : ""}`}>
        {links.map(([href, label]) => (
          <Link key={href} href={href} aria-current={pathname === href ? "page" : undefined} onClick={() => setOpen(false)}>{label}</Link>
        ))}
      </div>
      <button type="button" className="theme-toggle" onClick={toggleTheme} aria-label="Cambiar entre modo claro y oscuro" title="Cambiar tema">
        <span className="theme-moon" aria-hidden="true">☾</span><span className="theme-sun" aria-hidden="true">☀</span>
      </button>
      <Link className="primary-button public-login" href="/login" onClick={() => setOpen(false)}>Ingresar</Link>
      <button ref={menuButton} type="button" className="public-menu-toggle" aria-expanded={open} aria-controls="public-navigation" aria-label={open ? "Cerrar menú" : "Abrir menú"} onClick={() => setOpen(!open)}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d={open ? "M6 6l12 12M6 18L18 6" : "M4 6h16M4 12h16M4 18h16"} /></svg>
      </button>
    </nav>
  );
}
