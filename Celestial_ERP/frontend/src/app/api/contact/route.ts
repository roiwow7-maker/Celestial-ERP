import nodemailer from "nodemailer";
export const runtime = "nodejs";
export async function POST(request: Request) {
  const data = await request.formData();
  const name = String(data.get("name") ?? "").trim(); const email = String(data.get("email") ?? "").trim(); const type = String(data.get("type") ?? "contact");
  if (!name || !email || !email.includes("@")) return Response.json({ error: "Completa nombre y correo válido." }, { status: 400 });
  if (!process.env.SMTP_HOST || !process.env.SMTP_USER || !process.env.SMTP_PASSWORD || !process.env.CONTACT_TO) return Response.json({ error: "El correo aún no está configurado en este entorno." }, { status: 503 });
  const transporter = nodemailer.createTransport({ host: process.env.SMTP_HOST, port: Number(process.env.SMTP_PORT ?? 587), secure: process.env.SMTP_SECURE === "true", auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD } });
  const lines = [...data.entries()].filter(([key]) => key !== "cv").map(([key, value]) => `${key}: ${String(value)}`).join("\n");
  const attachments = [];
  const cv = data.get("cv");
  if (cv instanceof File && cv.size) {
    const allowed = /\.(pdf|doc|docx)$/i.test(cv.name);
    if (!allowed || cv.size > 10 * 1024 * 1024) return Response.json({ error: "El documento debe ser PDF, DOC o DOCX y pesar menos de 10 MB." }, { status: 400 });
    attachments.push({ filename: cv.name, content: Buffer.from(await cv.arrayBuffer()) });
  }
  await transporter.sendMail({ from: process.env.SMTP_FROM ?? process.env.SMTP_USER, to: process.env.CONTACT_TO, replyTo: email, subject: `${type === "career" ? "Postulación" : "Contacto"} Celestial ERP · ${name}`, text: lines, attachments });
  return Response.json({ ok: true });
}
