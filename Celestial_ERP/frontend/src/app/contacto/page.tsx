"use client";

import { useState, type FormEvent } from "react";
import { isValidRut } from "@/lib/rut";

export default function ContactPage() {
  const [rut, setRut] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (rut && !isValidRut(rut)) {
      setMessage("El RUT no es válido.");
      return;
    }
    setMessage("Enviando…");
    const response = await fetch("/api/contact", { method: "POST", body: new FormData(event.currentTarget) });
    const result = await response.json();
    setMessage(response.ok ? "Consulta enviada correctamente." : result.error ?? "No fue posible enviar la consulta.");
    if (response.ok) event.currentTarget.reset();
  }

  return (
    <main className="public-inner">
      <a href="/" className="public-back">← Celestial ERP</a>
      <span className="eyebrow">CONTACTO</span>
      <h1>Conversemos sobre la operación de tu empresa.</h1>
      <p className="inner-lead">Escríbenos para conocer la plataforma, solicitar una demostración o habilitar un nuevo dominio institucional.</p>
      <form className="contact-form" onSubmit={submit} encType="multipart/form-data">
        <input type="hidden" name="type" value="contact" />
        <label>Nombre completo<input name="name" required /></label>
        <label>Correo institucional<input name="email" type="email" required /></label>
        <label>RUT de empresa o persona<input name="rut" value={rut} onChange={(event) => setRut(event.target.value)} placeholder="76.123.456-7" /></label>
        <label>Edad<input name="age" type="number" min="18" max="100" /></label>
        <label>Género<select name="gender"><option value="">Prefiero no indicarlo</option><option>Masculino</option><option>Femenino</option><option>Otro</option></select></label>
        <label>Documento adicional (opcional)<input name="cv" type="file" accept=".pdf,.doc,.docx" /></label>
        <label>Mensaje<textarea name="message" required rows={5} /></label>
        {message && <div className={message.includes("correctamente") ? "alert-success" : "alert-error"}>{message}</div>}
        <button className="primary-button">Enviar consulta</button>
      </form>
    </main>
  );
}
