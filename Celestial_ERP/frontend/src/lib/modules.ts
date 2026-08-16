export type ErpView = {
  label: string;
  path: string;
  description?: string;
};

export type ErpModule = {
  id: string;
  label: string;
  shortLabel: string;
  accent: string;
  views: ErpView[];
};

export const erpModules: ErpModule[] = [
  {
    id: "inicio",
    label: "Inicio y operación",
    shortLabel: "Inicio",
    accent: "#8b5cf6",
    views: [
      { label: "Portal principal", path: "/applet/", description: "Resumen general del ERP" },
      { label: "Módulos", path: "/applet/modules/" },
      { label: "Kanban", path: "/applet/kanban/" },
      { label: "Estado del sistema", path: "/applet/system-status/" },
    ],
  },
  {
    id: "remuneraciones",
    label: "RR.HH. y remuneraciones",
    shortLabel: "Remuneraciones",
    accent: "#06b6d4",
    views: [
      { label: "Dashboard", path: "/remuneraciones/" },
      { label: "Trabajadores", path: "/remuneraciones/trabajadores/" },
      { label: "Períodos", path: "/remuneraciones/periodos/" },
      { label: "Ítems", path: "/remuneraciones/items/" },
      { label: "Liquidaciones", path: "/remuneraciones/liquidaciones/" },
      { label: "Movimientos", path: "/remuneraciones/movimientos/" },
      { label: "Reportes", path: "/reportes/" },
      { label: "Cargas ETL", path: "/cargas/" },
    ],
  },
  {
    id: "asistencia",
    label: "Asistencia",
    shortLabel: "Asistencia",
    accent: "#22c55e",
    views: [
      { label: "Dashboard", path: "/asistencia/" },
      { label: "Registros", path: "/asistencia/registros/" },
      { label: "Nuevo registro", path: "/asistencia/registros/nuevo/" },
      { label: "Informe mensual", path: "/asistencia/mensual/" },
    ],
  },
  {
    id: "contabilidad",
    label: "Contabilidad",
    shortLabel: "Contabilidad",
    accent: "#f59e0b",
    views: [
      { label: "Dashboard", path: "/contabilidad/" },
      { label: "Plan de cuentas", path: "/contabilidad/plan-cuentas/" },
      { label: "Centros de costo", path: "/contabilidad/centros-costo/" },
      { label: "Mapeos", path: "/contabilidad/mapeos/" },
      { label: "Asientos", path: "/contabilidad/asientos/" },
      { label: "Generar asiento de remuneraciones", path: "/contabilidad/asientos/generar-remuneraciones/" },
      { label: "Reportes", path: "/contabilidad/reportes/" },
    ],
  },
  {
    id: "inventario",
    label: "Inventario",
    shortLabel: "Inventario",
    accent: "#3b82f6",
    views: [
      { label: "Dashboard", path: "/inventario/" },
      { label: "Productos", path: "/inventario/productos/" },
      { label: "Bodegas", path: "/inventario/bodegas/" },
      { label: "Stock", path: "/inventario/stock/" },
      { label: "Movimientos", path: "/inventario/movimientos/" },
      { label: "Valorización", path: "/inventario/valorizacion/" },
    ],
  },
  {
    id: "comercio",
    label: "Compras y ventas",
    shortLabel: "Comercio",
    accent: "#ec4899",
    views: [
      { label: "Dashboard", path: "/comercio/" },
      { label: "Proveedores", path: "/comercio/proveedores/" },
      { label: "Clientes", path: "/comercio/clientes/" },
      { label: "Órdenes de compra", path: "/comercio/compras/" },
      { label: "Órdenes de venta", path: "/comercio/ventas/" },
      { label: "Reportes", path: "/comercio/reportes/" },
    ],
  },
  {
    id: "administracion",
    label: "Administración",
    shortLabel: "Administración",
    accent: "#64748b",
    views: [
      { label: "Panel administrativo", path: "/applet/admin-panel/" },
      { label: "Seguridad y usuarios", path: "/applet/security/" },
      { label: "Auditoría", path: "/applet/audit/" },
      { label: "Respaldos", path: "/applet/backups/" },
      { label: "Django Admin", path: "/admin/" },
      { label: "Catálogo API", path: "/api/" },
    ],
  },
];
