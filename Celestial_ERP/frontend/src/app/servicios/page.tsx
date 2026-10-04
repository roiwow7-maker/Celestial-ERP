export default function ServicesPage() {
  return (
    <main className="public-inner">
      <a href="/" className="public-back">← Celestial ERP</a>
      <span className="eyebrow">SERVICIOS</span>
      <h1>Un sistema completo, activado por módulos.</h1>
      <p className="inner-lead">Celestial ERP concentra la información de tu empresa en un entorno seguro. Puedes comenzar con un módulo y habilitar nuevas capacidades cuando el equipo las necesite.</p>
      <div className="inner-grid">
        <article><h2>Remuneraciones</h2><p>Centraliza trabajadores, contratos, períodos, liquidaciones y movimientos. El historial ETL queda trazable para revisar cambios y preparar procesos mensuales con menos trabajo manual.</p></article>
        <article><h2>Asistencia</h2><p>Registra jornadas, atrasos, ausencias y horas extra. Los reportes mensuales se conectan con remuneraciones para reducir duplicidad y detectar inconsistencias antes del cierre.</p></article>
        <article><h2>Contabilidad y finanzas</h2><p>Organiza plan de cuentas, centros de costo, mapeos y asientos. Los reportes entregan una lectura clara de ingresos, gastos y resultados para apoyar decisiones.</p></article>
        <article><h2>Inventario y comercio</h2><p>Administra productos, bodegas, stock, proveedores, clientes, compras y ventas. Cada movimiento mantiene su trazabilidad y respeta los permisos asignados a cada rol.</p></article>
        <article><h2>Multiempresa</h2><p>Cada empresa opera con su propia base de datos y configuración. El acceso se detecta por correo institucional y los módulos pueden habilitarse de manera independiente por entidad.</p></article>
        <article><h2>Seguridad y auditoría</h2><p>Las sesiones, permisos y operaciones quedan protegidos por controles del backend. La separación por empresa reduce el alcance de un incidente y facilita respaldos independientes.</p></article>
      </div>
      <section className="inner-callout"><h2>Una implementación gradual</h2><p>Partimos por la operación que más valor entrega hoy, medimos el resultado y sumamos el siguiente módulo sin cambiar la forma en que tu equipo trabaja.</p><a className="primary-button" href="/contacto">Conversemos sobre tu empresa</a></section>
    </main>
  );
}
