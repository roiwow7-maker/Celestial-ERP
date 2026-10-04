export function normalizeRut(value: string): string { return value.replace(/[^0-9kK]/g, "").toUpperCase(); }
export function isValidRut(value: string): boolean {
  const rut = normalizeRut(value); if (!/^\d{7,8}[0-9K]$/.test(rut)) return false;
  const body = rut.slice(0, -1); const expected = rut.slice(-1); let factor = 2; let sum = 0;
  for (let index = body.length - 1; index >= 0; index -= 1) { sum += Number(body[index]) * factor; factor = factor === 7 ? 2 : factor + 1; }
  const remainder = 11 - (sum % 11); const check = remainder === 11 ? "0" : remainder === 10 ? "K" : String(remainder);
  return check === expected;
}
