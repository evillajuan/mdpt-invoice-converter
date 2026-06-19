const SESSION_COOKIE = 'mdpt_session';
const ALGORITHM = { name: 'HMAC', hash: 'SHA-256' };

function getSecret(): string {
  const s = process.env.SESSION_SECRET;
  if (!s) throw new Error('SESSION_SECRET env var is not set');
  return s;
}

async function importKey(secret: string): Promise<CryptoKey> {
  const enc = new TextEncoder();
  return crypto.subtle.importKey('raw', enc.encode(secret), ALGORITHM, false, ['sign', 'verify']);
}

export async function createSessionToken(): Promise<string> {
  const key = await importKey(getSecret());
  const payload = Date.now().toString();
  const sig = await crypto.subtle.sign(ALGORITHM, key, new TextEncoder().encode(payload));
  const sigHex = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('');
  return `${payload}.${sigHex}`;
}

export async function verifySessionToken(token: string): Promise<boolean> {
  try {
    const [payload, sigHex] = token.split('.');
    if (!payload || !sigHex) return false;
    const key = await importKey(getSecret());
    const sigBytes = new Uint8Array(sigHex.match(/.{2}/g)!.map(h => parseInt(h, 16)));
    return crypto.subtle.verify(ALGORITHM, key, sigBytes, new TextEncoder().encode(payload));
  } catch {
    return false;
  }
}

export { SESSION_COOKIE };
