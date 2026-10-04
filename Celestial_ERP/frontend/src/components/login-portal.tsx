"use client";

import Link from "next/link";
import { useRef, useState, type FormEvent } from "react";

type LoginCompany = { id: string; name: string; domains: string[] };

export function LoginPortal({ companies, initialCompany }: { companies: LoginCompany[]; initialCompany?: string }) {
  const [identifier, setIdentifier] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const submitting = useRef(false);
  const domain = identifier.trim().toLowerCase().split("@")[1];
  const matches = companies.filter(company => company.domains.includes(domain));
  // Local usernames keep the company from their existing access link. The
  // historical company remains the default for unscoped local accounts.
  const localCompany = companies.find(company => company.id === (initialCompany ?? "default")) ?? (companies.length === 1 ? companies[0] : undefined);
  const company = identifier.includes("@") ? (matches.length === 1 ? matches[0] : undefined) : localCompany;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    setError("");
    if (!company || !identifier.trim()) {
      setError("No pudimos identificar tu empresa. Revisa tu correo institucional o solicita tu enlace de acceso al administrador.");
      return;
    }
    const data = new FormData(event.currentTarget);
    submitting.current = true;
    setBusy(true);
    const prefix = `/backend/company/${encodeURIComponent(company.id)}/api/v1`;
    try {
      // Obtain this company's CSRF cookie before submitting credentials.
      const sessionResponse = await fetch(`${prefix}/session/`, { credentials: "same-origin", cache: "no-store", signal: AbortSignal.timeout(15000) });
      if (!sessionResponse.ok) throw new Error("El servicio de tu empresa no está disponible. Intenta nuevamente en unos momentos.");
      const session = await sessionResponse.json();
      if (session.company?.id !== company.id) throw new Error("No fue posible verificar el acceso de tu empresa.");
      const cookieName = `erp_${company.id}_csrftoken=`;
      const token = document.cookie.split(";").map(part => part.trim()).find(part => part.startsWith(cookieName))?.slice(cookieName.length);
      if (!token) throw new Error("No fue posible preparar la sesión. Comprueba que el navegador permita cookies e inténtalo otra vez.");
      const response = await fetch(`${prefix}/login/`, {
        method: "POST", credentials: "same-origin", signal: AbortSignal.timeout(15000),
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ username: identifier.trim(), password: data.get("password") }),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error ?? "No fue posible iniciar sesión. Inténtalo nuevamente.");
      if (!result.authenticated || result.company?.id !== company.id) throw new Error("No fue posible verificar el acceso de tu empresa.");
      // A full navigation clears all state and requests of the previous tenant.
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      window.location.assign(`/portal?company=${encodeURIComponent(company.id)}`);
    } catch (reason) {
      setError(reason instanceof Error && !["TimeoutError", "TypeError"].includes(reason.name) ? reason.message : "No pudimos conectar con tu empresa. Revisa la conexión e inténtalo nuevamente.");
      submitting.current = false;
      setBusy(false);
    }
  }

  return (
    <main className="public-inner access-page">
      <section className="access-card" aria-labelledby="login-title">
        <div className="access-welcome">
          <span className="eyebrow">CELESTIAL ERP</span>
          <h2>Tu equipo.<br />Tu empresa.<br />Un mismo espacio.</h2>
          <p>Vuelve a tu centro de gestión y continúa con lo que importa.</p>
          <div className="access-orbit" aria-hidden="true"><span>C</span></div>
          <span className="access-caption">Todo conectado, en tu órbita.</span>
        </div>
        <div className="access-form-panel">
          <Link href="/" className="public-back">← Volver al inicio</Link>
          <span className="eyebrow">BIENVENIDO A TU ESPACIO</span>
          <h1 id="login-title">Iniciar sesión</h1>
          <p>Ingresa con tu cuenta de empresa.</p>
          <form className="access-form" onSubmit={submit} aria-busy={busy}>
            <fieldset disabled={busy}>
              <label htmlFor="login-identifier">Correo institucional o usuario</label>
              <input id="login-identifier" name="username" autoComplete="username" autoCapitalize="none" spellCheck={false} required maxLength={254} placeholder="nombre@tuempresa.cl" value={identifier} onChange={event => { setIdentifier(event.target.value); setError(""); }} aria-describedby="login-company" />
              <p id="login-company" className="access-company" aria-live="polite">{identifier.trim() && company ? `${identifier.includes("@") ? "Empresa" : "Acceso con usuario local"}: ${company.name}` : "Tu correo institucional identifica automáticamente tu empresa."}</p>
              <label htmlFor="login-password">Contraseña</label>
              <div className="access-password">
                <input id="login-password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" required />
                <button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"} aria-pressed={showPassword}>{showPassword ? "Ocultar" : "Mostrar"}</button>
              </div>
            </fieldset>
            {error && <div className="alert-error" role="alert">{error}</div>}
            <button className="primary-button access-submit" type="submit" disabled={busy}>{busy ? "Ingresando…" : "Iniciar sesión"}</button>
            <p className="access-help">¿Necesitas una cuenta o recuperar el acceso? Contacta al administrador de tu empresa o <Link href="/contacto">escríbenos</Link>.</p>
          </form>
        </div>
      </section>
    </main>
  );
}
