import { PublicNavbar } from "./public-navbar";

export function CompanyEntry() {
  return (
    <main className="public-home">
      <PublicNavbar />
      <section className="public-hero">
        <div>
          <span className="eyebrow">GESTIÓN EMPRESARIAL LOCAL Y SEGURA</span>
          <h1>Todo tu negocio en un solo centro de control.</h1>
          <p>Remuneraciones, asistencia, contabilidad, inventario y comercio conectados a la operación real de cada empresa.</p>
          <a className="primary-button hero-cta" href="/login">Ingresar al portal</a>
        </div>
        <div className="hero-card"><span>OPERACIÓN EN TIEMPO REAL</span><strong>ERP modular</strong><small>Cada empresa activa solo lo que necesita.</small><div className="hero-bars"><i /><i /><i /><i /></div></div>
      </section>
      <section className="service-section">
        <div><span className="eyebrow">SERVICIOS</span><h2>Una plataforma que se adapta a cada empresa.</h2><p>Activa las capacidades que tu equipo usa hoy y agrega nuevas funciones cuando el negocio crezca.</p></div>
        <div className="service-grid">
          <article><b>01</b><h3>Personas y remuneraciones</h3><p>Trabajadores, contratos, liquidaciones, asistencia y cargas ETL en un flujo controlado y trazable.</p></article>
          <article><b>02</b><h3>Finanzas y control</h3><p>Plan de cuentas, centros de costo, mapeos, asientos y reportes para decidir con datos confiables.</p></article>
          <article><b>03</b><h3>Operación comercial</h3><p>Inventario, compras, ventas, bodegas y proveedores con permisos por rol y seguimiento de cada movimiento.</p></article>
        </div>
        <a className="text-link" href="/servicios">Conoce todos los módulos →</a>
      </section>
      <section className="access-section">
        <div><span className="eyebrow">ACCESO A TU EMPRESA</span><h2>Tu correo identifica tu empresa.</h2><p>Entra con tu correo institucional y contraseña desde nuestra página de acceso. Celestial ERP te lleva al espacio de tu empresa.</p><a className="primary-button hero-cta" href="/login">Ir a iniciar sesión</a></div>
      </section>
      <footer className="public-footer">© {new Date().getFullYear()} Celestial ERP · Gestión modular para empresas.</footer>
    </main>
  );
}
