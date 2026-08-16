"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Session = { authenticated: boolean; user?: { name: string }; permissions?: string[] };
type Option = { value: string; label: string };
type Field = { name: string; label: string; required: boolean; type: string; help_text: string; options?: Option[] };
type Item = Record<string, string | number | boolean | null> & { id: number; label: string };
type Resource = { key: string; title: string; module: string; fields: Field[]; items: Item[]; total: number; can_add: boolean };
type CatalogItem = { key: string; title: string; module: string; count: number };

const groups = [
  { label: "Remuneraciones", color: "#06b6d4", items: [["employees", "Trabajadores"], ["periods", "Períodos"], ["payroll-items", "Ítems"], ["payroll-summaries", "Liquidaciones"], ["payroll-entries", "Movimientos"]] },
  { label: "Asistencia", color: "#22c55e", items: [["attendance", "Registros"]] },
  { label: "Contabilidad", color: "#f59e0b", items: [["accounts", "Plan de cuentas"], ["cost-centers", "Centros de costo"], ["account-mappings", "Mapeos"]] },
  { label: "Inventario", color: "#3b82f6", items: [["products", "Productos"], ["warehouses", "Bodegas"], ["stock-movements", "Movimientos de stock"]] },
  { label: "Compras y ventas", color: "#ec4899", items: [["suppliers", "Proveedores"], ["customers", "Clientes"], ["purchases", "Compras"], ["sales", "Ventas"]] },
] as const;

const api = (path: string) => `/backend/api/v1/${path}`;
const specialViews = new Set(["reports", "uploads", "users"]);
const csrf = () => document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] ?? "";

async function jsonFetch(path: string, init?: RequestInit) {
  const response = await fetch(api(path), { credentials: "same-origin", ...init, headers: { "Content-Type": "application/json", "X-CSRFToken": csrf(), ...init?.headers } });
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error(response.status === 403 ? "Tu usuario no tiene permiso para abrir este módulo." : `El servidor respondió con un error (${response.status}).`);
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || Object.values(data.errors || {}).flat().map((v: unknown) => JSON.stringify(v)).join(" ") || "No fue posible completar la operación.");
  return data;
}

export function ErpShell() {
  const [session, setSession] = useState<Session | null>(null);
  const [active, setActive] = useState("dashboard");
  const [resource, setResource] = useState<Resource | null>(null);
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState<Item | null | undefined>(undefined);
  const [mobileMenu, setMobileMenu] = useState(false);

  const load = useCallback(async (key = active, query = search) => {
    setBusy(true); setError("");
    try { setResource(await jsonFetch(`resources/${key}/?q=${encodeURIComponent(query)}`)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Error de conexión."); }
    finally { setBusy(false); }
  }, [active, search]);

  useEffect(() => { jsonFetch("session/").then(setSession).catch(() => setSession({ authenticated: false })); }, []);
  useEffect(() => {
    if (!session?.authenticated) return;
    const task = window.setTimeout(() => {
      if (active === "dashboard") {
        setBusy(true);
        jsonFetch("catalog/").then((data) => setCatalog(data.resources)).catch((reason) => setError(reason.message)).finally(() => setBusy(false));
      } else if (!specialViews.has(active)) void load(active, "");
    }, 0);
    return () => window.clearTimeout(task);
  }, [active, session?.authenticated]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!session) return <Centered message="Iniciando Celestial ERP…" />;
  if (!session.authenticated) return <Login onLogin={setSession} />;

  const selectResource = (key: string) => { setActive(key); setSearch(""); setEditing(undefined); setMobileMenu(false); };
  return (
    <main className="native-shell">
      {mobileMenu && <button className="mobile-overlay" aria-label="Cerrar menú" onClick={() => setMobileMenu(false)} />}
      <aside className={`native-sidebar ${mobileMenu ? "mobile-open" : ""}`}>
        <div className="brand"><div className="brand-mark">C</div><div><strong>Celestial</strong><span>ERP · Frontend Next.js</span></div></div>
        <nav className="native-nav">
          <section><button className={active === "dashboard" ? "active" : ""} onClick={() => selectResource("dashboard")}>Resumen general</button></section>
          {groups.map((group) => <section key={group.label}><h3><i style={{ background: group.color }} />{group.label}</h3>{group.items.map(([key, label]) => <button className={active === key ? "active" : ""} key={key} onClick={() => selectResource(key)}>{label}</button>)}</section>)}
          <section><h3><i style={{ background: "#8b5cf6" }} />Análisis y operación</h3><button className={active === "reports" ? "active" : ""} onClick={() => selectResource("reports")}>Reportes PDF</button>{session.permissions?.includes("DATA_scope.upload_payroll_data") && <button className={active === "uploads" ? "active" : ""} onClick={() => selectResource("uploads")}>Carga masiva ETL</button>}</section>
          {session.permissions?.includes("Applet.access_security_module") && <section><h3><i style={{ background: "#ef4444" }} />Administración</h3><button className={active === "users" ? "active" : ""} onClick={() => selectResource("users")}>Usuarios y roles</button></section>}
        </nav>
        <div className="user-card"><span>{session.user?.name}</span><button onClick={async () => { await jsonFetch("logout/", { method: "POST", body: "{}" }); setSession({ authenticated: false }); }}>Salir</button></div>
      </aside>
      <section className="native-workspace">
        <header className="native-header no-print"><button className="mobile-menu-button" type="button" aria-label="Abrir menú" aria-expanded={mobileMenu} onClick={() => setMobileMenu(true)}>☰</button><div className="mobile-heading"><small>GESTIÓN / {resource?.module ?? "ERP"}</small><h1>{active === "dashboard" ? "Resumen general" : active === "reports" ? "Reportes" : active === "uploads" ? "Carga masiva ETL" : active === "users" ? "Usuarios y roles" : resource?.title ?? "Cargando…"}</h1></div>{active !== "dashboard" && !specialViews.has(active) && <div className="header-actions"><form onSubmit={(event) => { event.preventDefault(); void load(); }}><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar…" aria-label="Buscar registros" /></form>{resource?.can_add && <button className="primary-button" onClick={() => setEditing(null)}>+ Nuevo</button>}</div>}</header>
        <div className="native-content">
          {error && <div className="alert-error">{error}<button onClick={() => void load()}>Reintentar</button></div>}
          {busy ? <Centered message="Consultando datos…" /> : active === "dashboard" ? <Dashboard items={catalog} onOpen={selectResource} /> : active === "reports" ? <ReportsView /> : active === "uploads" ? <UploadsView /> : active === "users" ? <UsersView /> : resource && <ResourceTable resource={resource} onEdit={setEditing} />}
        </div>
      </section>
      {editing !== undefined && resource && <ResourceForm resource={resource} item={editing} onClose={() => setEditing(undefined)} onSaved={() => { setEditing(undefined); void load(); }} />}
    </main>
  );
}

function Dashboard({ items, onOpen }: { items: CatalogItem[]; onOpen: (key: string) => void }) {
  const total = items.reduce((sum, item) => sum + item.count, 0);
  return <div className="dashboard-view"><section className="welcome-panel"><div><small>BUEN DÍA</small><h2>Centro de gestión Celestial</h2><p>Datos operativos en tiempo real, protegidos por los permisos de Django.</p></div><div className="hero-number"><strong>{total.toLocaleString("es-CL")}</strong><span>registros administrados</span></div></section><div className="metric-grid">{items.map((item) => <button key={item.key} onClick={() => onOpen(item.key)}><span>{item.module}</span><strong>{item.count.toLocaleString("es-CL")}</strong><p>{item.title}</p><i>Abrir módulo →</i></button>)}</div></div>;
}

type ReportFilter = { name:string; label:string; type:string; options?: (string | Option | { value:number; label:string })[] };
type ChartData = { title:string; series:{ label:string; value:number|string }[] };
type ReportSection = { key: string; title: string; summary: Record<string, unknown>; columns: string[]; rows: Record<string, unknown>[]; charts?:ChartData[]; filters?:ReportFilter[] };
function ReportsView() {
  const [sections, setSections] = useState<ReportSection[]>([]); const [active, setActive] = useState(""); const [error, setError] = useState(""); const [busy,setBusy]=useState(false); const [query,setQuery]=useState("");
  const fetchReports=useCallback((parameters="")=>{setBusy(true);return jsonFetch(`reports/${parameters?`?${parameters}`:""}`).then((data)=>{setSections(data.sections);setActive((current:string)=>current||data.sections[0]?.key||"");}).catch((reason)=>setError(reason.message)).finally(()=>setBusy(false));},[]);
  useEffect(() => { const task=window.setTimeout(()=>void fetchReports(),0); return()=>window.clearTimeout(task); }, [fetchReports]);
  const report = sections.find((item) => item.key === active);
  function filter(event:FormEvent<HTMLFormElement>){event.preventDefault();const data=new FormData(event.currentTarget);const params=new URLSearchParams();data.forEach((value,key)=>{if(value){const normalized=(key==="period_from"||key==="period_to")?String(value).replace("-",""):String(value);params.set(key,normalized);}});setQuery(params.toString());void fetchReports(params.toString());}
  return <div className="report-page"><div className="report-toolbar no-print"><div>{sections.map((item) => <button className={active === item.key ? "active" : ""} key={item.key} onClick={() => {setActive(item.key);setQuery("");void fetchReports();}}>{item.title}</button>)}</div><button className="primary-button" onClick={() => window.print()}>Imprimir / Guardar PDF</button></div>{report?.filters&&<form className="report-filters no-print" key={active} onSubmit={filter}>{report.filters.map((field)=><label key={field.name}>{field.label}{field.type==="select"?<select name={field.name}><option value="">Todos</option>{field.options?.map((raw)=>{const option=typeof raw==="string"?{value:raw,label:raw}:raw;return <option key={String(option.value)} value={option.value}>{option.label}</option>})}</select>:<input name={field.name} type={field.type}/>}</label>)}<button className="primary-button" disabled={busy}>{busy?"Aplicando…":"Aplicar filtros"}</button><button type="button" className="secondary-button" onClick={()=>{setQuery("");void fetchReports();}}>Limpiar</button></form>}{error && <div className="alert-error">{error}</div>}{report && <article className="print-report"><header><div className="brand-mark">C</div><div><small>CELESTIAL ERP · REPORTE OFICIAL</small><h2>{report.title}</h2><p>Generado el {new Date().toLocaleString("es-CL")}{query?" · Reporte filtrado":""}</p></div></header><div className="report-metrics">{Object.entries(report.summary).map(([key, value]) => <div key={key}><span>{humanize(key)}</span><strong>{formatValue(value)}</strong></div>)}</div>{report.charts&&<div className="charts-grid">{report.charts.map((chart)=><ReportChart chart={chart} key={chart.title}/>)}</div>}<div className="table-scroll"><table><thead><tr>{report.columns.map((column) => <th key={column}>{humanize(column)}</th>)}</tr></thead><tbody>{report.rows.map((row, index) => <tr key={index}>{report.columns.map((column) => <td key={column}>{formatValue(row[column])}</td>)}</tr>)}</tbody></table></div><footer>Celestial ERP · Documento generado electrónicamente</footer></article>}</div>;
}

function ReportChart({chart}:{chart:ChartData}){const values=chart.series.map((item)=>Math.abs(Number(item.value)||0));const max=Math.max(...values,1);return <section className="report-chart"><h3>{chart.title}</h3><div className="chart-bars">{chart.series.slice(-18).map((item,index)=>{const value=Math.abs(Number(item.value)||0);return <div className="chart-column" key={`${item.label}-${index}`}><span title={`${item.label}: ${formatNumber(value)}`} style={{height:`${Math.max((value/max)*150,2)}px`}}/><small>{String(item.label).slice(0,10)}</small></div>})}</div></section>}
function formatNumber(value:number){return new Intl.NumberFormat("es-CL",{maximumFractionDigits:0}).format(value)}

function UploadsView() {
  const [history, setHistory] = useState<Record<string, unknown>[]>([]); const [job, setJob] = useState<Record<string, unknown> | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const refresh = useCallback(() => jsonFetch("uploads/").then((data) => setHistory(data.uploads)).catch((reason) => setError(reason.message)), []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { if (!job?.run_id || !["queued", "running"].includes(String(job.status))) return; const timer = window.setInterval(() => jsonFetch(`uploads/${job.run_id}/`).then(setJob).catch((reason) => setError(reason.message)), 2000); return () => window.clearInterval(timer); }, [job]);
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setBusy(true); setError(""); const data = new FormData(event.currentTarget); try { const response = await fetch(api("uploads/"), { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrf() }, body: data }); const payload = await response.json(); if (!response.ok) throw new Error(payload.error); setJob(payload); void refresh(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falló la carga."); } finally { setBusy(false); } }
  return <div className="operations-grid"><form className="operation-card" onSubmit={submit}><h2>Nueva carga masiva</h2><p>Procesa CSV, XLSX o XLS con el pipeline ETL oficial.</p>{error && <div className="alert-error">{error}</div>}<label className="drop-zone">Seleccionar archivo<input name="file" type="file" accept=".csv,.xlsx,.xls" required /></label><div className="form-grid compact"><label>Formato<select name="source_format" defaultValue="auto"><option value="auto">Detectar automáticamente</option><option value="horizontal">Horizontal</option><option value="vertical">Vertical</option></select></label><label>RUT empresa<input name="rut_empresa" /></label><label className="check-field"><input name="import" value="true" type="checkbox" />Importar al ERP</label><label className="check-field"><input name="excel" value="true" type="checkbox" />Generar Excel</label><label className="check-field danger"><input name="clear" value="true" type="checkbox" />Limpiar datos antes</label></div><button className="primary-button" disabled={busy}>{busy ? "Subiendo…" : "Iniciar procesamiento"}</button>{job && <JobStatus job={job} />}</form><section className="operation-card"><h2>Historial de importaciones</h2><div className="history-list">{history.map((item) => <div key={String(item.id)}><span className={`status-badge ${item.status}`}>{String(item.status)}</span><strong>{new Date(String(item.created_at)).toLocaleString("es-CL")}</strong><small>{String(item.entry_count)} movimientos · {String(item.summary_count)} liquidaciones</small></div>)}</div></section></div>;
}
function JobStatus({ job }: { job: Record<string, unknown> }) { return <div className="job-status"><strong>Estado: {String(job.status)}</strong><span>{String(job.input_name ?? "")}</span>{Boolean(job.error) && <p>{String(job.error)}</p>}{Array.isArray(job.downloads) && job.downloads.map((item: { label: string; url: string }) => <a key={item.url} href={`/backend${item.url}`}>{item.label}</a>)}</div>; }

type UserRow = { id:number; username:string; name:string; email:string; active:boolean; staff:boolean; superuser:boolean; roles:string[]; last_login:string|null };
function UsersView() {
  const [users, setUsers] = useState<UserRow[]>([]); const [roles, setRoles] = useState<string[]>([]); const [selected, setSelected] = useState<UserRow|null>(null); const [creating,setCreating]=useState(false); const [error,setError]=useState("");
  const load = useCallback(() => jsonFetch("users/").then((data) => { setUsers(data.users); setRoles(data.roles); }).catch((reason) => setError(reason.message)), []); useEffect(() => { void load(); }, [load]);
  async function save(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!selected)return;const data=new FormData(event.currentTarget);try{await jsonFetch(`users/${selected.id}/`,{method:"PATCH",body:JSON.stringify({is_active:data.has("active"),is_staff:data.has("staff"),roles:data.getAll("roles"),password:data.get("password")})});setSelected(null);void load();}catch(reason){setError(reason instanceof Error?reason.message:"No fue posible guardar.");}}
  async function create(event:FormEvent<HTMLFormElement>){event.preventDefault();const data=new FormData(event.currentTarget);try{await jsonFetch("users/",{method:"POST",body:JSON.stringify({username:data.get("username"),password:data.get("password"),first_name:data.get("first_name"),last_name:data.get("last_name"),email:data.get("email"),roles:data.getAll("roles")})});setCreating(false);void load();}catch(reason){setError(reason instanceof Error?reason.message:"No fue posible crear el usuario.");}}
  const roleFields=(selectedRoles:string[])=><fieldset><legend>Roles</legend>{roles.map((role)=><label className="check-field" key={role}><input name="roles" value={role} type="checkbox" defaultChecked={selectedRoles.includes(role)}/>{role}</label>)}</fieldset>;
  return <div className="data-card">{error&&<div className="alert-error">{error}</div>}<div className="admin-summary"><div><strong>{users.length}</strong><span>usuarios registrados</span></div><p>El acceso efectivo combina estado de cuenta, roles y permisos Django.</p><button className="primary-button" onClick={()=>setCreating(true)}>+ Crear usuario</button></div><div className="user-grid">{users.map((user)=><button key={user.id} onClick={()=>setSelected(user)}><span className={`avatar ${user.active?"":"inactive"}`}>{user.username[0]?.toUpperCase()}</span><div><strong>{user.name||user.username}</strong><small>@{user.username} · {user.roles.join(", ")||"Sin rol"}</small></div><i>{user.active?"Activo":"Desactivado"}</i></button>)}</div>{selected&&<div className="modal-backdrop" onMouseDown={()=>setSelected(null)}><form className="resource-modal narrow" onSubmit={save} onMouseDown={(e)=>e.stopPropagation()}><header><div><small>CONTROL DE ACCESO</small><h2>{selected.username}</h2></div><button type="button" onClick={()=>setSelected(null)}>×</button></header><div className="form-grid compact"><label className="check-field"><input name="active" type="checkbox" defaultChecked={selected.active}/>Cuenta activa</label><label className="check-field"><input name="staff" type="checkbox" defaultChecked={selected.staff}/>Acceso administrativo</label><label>Nueva contraseña<input name="password" type="password" placeholder="Dejar vacío para conservar"/></label>{roleFields(selected.roles)}</div><footer><button className="primary-button">Guardar accesos</button></footer></form></div>}{creating&&<div className="modal-backdrop" onMouseDown={()=>setCreating(false)}><form className="resource-modal narrow" onSubmit={create} onMouseDown={(e)=>e.stopPropagation()}><header><div><small>NUEVA CUENTA</small><h2>Crear usuario</h2></div><button type="button" onClick={()=>setCreating(false)}>×</button></header><div className="form-grid compact"><label>Usuario<input name="username" required/></label><label>Contraseña inicial<input name="password" type="password" required/></label><label>Nombre<input name="first_name"/></label><label>Apellido<input name="last_name"/></label><label>Correo<input name="email" type="email"/></label>{roleFields([])}</div><footer><button className="primary-button">Crear cuenta</button></footer></form></div>}</div>;
}
function humanize(value:string){return value.replaceAll("__"," ").replaceAll("_"," ").replace(/^./,(letter)=>letter.toUpperCase());}

function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setBusy(true); setError(""); const form = new FormData(event.currentTarget); try { onLogin(await jsonFetch("login/", { method: "POST", body: JSON.stringify({ username: form.get("username"), password: form.get("password") }) })); } catch (reason) { setError(reason instanceof Error ? reason.message : "No fue posible ingresar."); } finally { setBusy(false); } }
  return <main className="login-screen"><form className="login-card" onSubmit={submit}><div className="brand-mark large">C</div><p>CELESTIAL ERP</p><h1>Bienvenido</h1><span>Ingresa con tu cuenta nominal del sistema</span>{error && <div className="alert-error">{error}</div>}<label>Usuario<input name="username" autoComplete="username" required /></label><label>Contraseña<input name="password" type="password" autoComplete="current-password" required /></label><button className="primary-button" disabled={busy}>{busy ? "Ingresando…" : "Iniciar sesión"}</button></form></main>;
}

function ResourceTable({ resource, onEdit }: { resource: Resource; onEdit: (item: Item) => void }) {
  const columns = useMemo(() => resource.fields.slice(0, 7), [resource]);
  return <div className="data-card resource-data"><div className="data-summary"><strong>{resource.total.toLocaleString("es-CL")}</strong><span>registros</span></div><div className="table-scroll"><table><thead><tr>{columns.map((field) => <th key={field.name}>{field.label}</th>)}<th /></tr></thead><tbody>{resource.items.map((item) => <tr key={item.id}>{columns.map((field) => <td data-label={field.label} key={field.name}>{formatValue(item[`${field.name}_label`] ?? item[field.name])}</td>)}<td className="row-action"><button className="table-action" onClick={() => onEdit(item)}>Editar registro</button></td></tr>)}</tbody></table>{resource.items.length === 0 && <div className="empty-state">No hay registros para mostrar.</div>}</div></div>;
}

function ResourceForm({ resource, item, onClose, onSaved }: { resource: Resource; item: Item | null; onClose: () => void; onSaved: () => void }) {
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setBusy(true); setError(""); const values: Record<string, FormDataEntryValue | boolean> = {}; const data = new FormData(event.currentTarget); for (const field of resource.fields) values[field.name] = field.type === "checkbox" ? data.has(field.name) : data.get(field.name) ?? ""; try { await jsonFetch(`resources/${resource.key}/${item ? `${item.id}/` : ""}`, { method: item ? "PUT" : "POST", body: JSON.stringify(values) }); onSaved(); } catch (reason) { setError(reason instanceof Error ? reason.message : "No fue posible guardar."); } finally { setBusy(false); } }
  return <div className="modal-backdrop" onMouseDown={onClose}><form className="resource-modal" onSubmit={submit} onMouseDown={(e) => e.stopPropagation()}><header><div><small>{item ? "EDITAR REGISTRO" : "NUEVO REGISTRO"}</small><h2>{resource.title}</h2></div><button type="button" onClick={onClose}>×</button></header>{error && <div className="alert-error">{error}</div>}<div className="form-grid">{resource.fields.map((field) => <FormField key={field.name} field={field} value={item?.[field.name]} />)}</div><footer><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button><button className="primary-button" disabled={busy}>{busy ? "Guardando…" : "Guardar"}</button></footer></form></div>;
}

function FormField({ field, value }: { field: Field; value: unknown }) { if (field.type === "checkbox") return <label className="check-field"><input name={field.name} type="checkbox" defaultChecked={Boolean(value)} />{field.label}</label>; return <label>{field.label}{field.type === "select" ? <select name={field.name} required={field.required} defaultValue={value == null ? "" : String(value)}><option value="">Seleccionar…</option>{field.options?.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : <input name={field.name} type={field.type === "datetime-local" ? "datetime-local" : field.type} required={field.required} defaultValue={value == null ? "" : String(value).slice(0, field.type === "datetime-local" ? 16 : undefined)} />}{field.help_text && <small>{field.help_text}</small>}</label>; }
function Centered({ message }: { message: string }) { return <div className="centered"><span className="spinner" />{message}</div>; }
function formatValue(value: unknown) { if (value === true) return "Sí"; if (value === false) return "No"; if (value == null || value === "") return "—"; return String(value); }
