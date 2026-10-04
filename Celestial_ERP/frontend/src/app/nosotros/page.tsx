export default function AboutPage() {
  return (
    <main className="public-inner">
      <a href="/" className="public-back">← Celestial ERP</a>
      <span className="eyebrow">NOSOTROS</span>
      <h1>Ordenamos la operación para que las empresas puedan crecer.</h1>
      <p className="inner-lead">Celestial ERP nace para entregar una gestión clara, modular y segura a empresas que necesitan conectar personas, finanzas y operación sin depender de planillas dispersas.</p>
      <section className="about-story">
        <h2>Una plataforma pensada para la realidad local</h2>
        <p>Construimos el sistema alrededor de los procesos que ocurren cada día: contratar, registrar asistencia, pagar, comprar, vender, controlar inventario y revisar resultados. La información se mantiene relacionada para que el equipo pueda pasar de una tarea a otra sin perder contexto.</p>
        <p>El diseño multiempresa permite que cada entidad tenga su propia base de datos, usuarios, dominio institucional y módulos activos. Así, una organización de servicios técnicos puede operar con una configuración distinta a una tienda o a una empresa de administración.</p>
      </section>
      <div className="inner-grid">
        <article><h2>Claridad</h2><p>Presentamos la información operativa con nombres comprensibles, indicadores útiles y recorridos simples para que cada persona encuentre lo que necesita.</p></article>
        <article><h2>Control</h2><p>Los permisos por rol, las sesiones protegidas y los registros de actividad ayudan a saber quién accede, qué cambia y cuándo ocurre cada operación.</p></article>
        <article><h2>Adaptabilidad</h2><p>Cada empresa activa solo los módulos que utiliza. La configuración puede crecer con el negocio sin obligar a todos los equipos a trabajar con funciones innecesarias.</p></article>
        <article><h2>Acompañamiento</h2><p>La implementación se realiza por etapas: levantamos el proceso, configuramos la entidad, validamos los datos y dejamos una base preparada para la siguiente mejora.</p></article>
      </div>
      <section className="inner-callout"><h2>¿Quieres revisar si encaja con tu operación?</h2><p>Cuéntanos cómo trabajan hoy y te ayudamos a identificar el primer módulo que conviene ordenar.</p><a className="primary-button" href="/contacto">Contactar al equipo</a></section>
    </main>
  );
}
