export async function onRequest(context) {
  const request = context.request;
  const ua = (request.headers.get("user-agent") || "").toLowerCase();
  if (ua.includes("curl") || ua.includes("wget") || ua.includes("httpie")) {
    const url = new URL(request.url);
    const pathParam = url.pathname.replace(/^\//, '').trim();
    if (pathParam && !isNaN(Number(pathParam))) {
      const num = Number(pathParam);
      const ms = num < 10000000000 ? num * 1000 : num;
      const d = new Date(ms);
      return new Response(`UTC: ${d.toISOString()}\nLocal (Brussels): ${d.toLocaleString('en-GB', { timeZone: 'Europe/Brussels' })}\nEpoch Seconds: ${Math.floor(ms / 1000)}\nEpoch Milliseconds: ${ms}\n`, {
        headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" }
      });
    }
    const now = Date.now();
    const sec = Math.floor(now / 1000);
    return new Response(`${sec}\n`, {
      headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" }
    });
  }
  return context.next();
}
