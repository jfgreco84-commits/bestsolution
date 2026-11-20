// Best Solution: exact-amount Square card checkout.
// The website sends the cart here. This builds a Square payment link for the exact
// order (items, WI sales tax when it applies) and hands the link back. The customer
// lands on Square's secure page with the total already filled in.
//
// Secrets (set in Supabase, never in this file):
//   SQUARE_ACCESS_TOKEN   required. Square production access token.
//   SQUARE_LOCATION_ID    optional. If missing, the first active location is used.
//
// Prices live here on purpose so nobody can change a price from their browser.
// KEEP THIS TABLE IN STEP WITH THE PRICES IN index.html.

const PRICES: Record<string, { name: string; price: number }> = {
  show100: { name: "$100 Show Special", price: 100 },
  b32L: { name: "32oz Polish + Large C5 (8oz)", price: 60 },
  b16L: { name: "16oz Polish + Large C5 (8oz)", price: 55 },
  b8L: { name: "8oz Polish + Large C5 (8oz)", price: 50 },
  b32S: { name: "32oz Polish + Small C5 (2oz)", price: 50 },
  b16S: { name: "16oz Polish + Small C5 (2oz)", price: 45 },
  b8S: { name: "8oz Polish + Small C5 (2oz)", price: 40 },
  b2S: { name: "2oz Polish + Small C5 (2oz)", price: 30 },
  gl15: { name: "Glasses Set", price: 20 },
  gl25: { name: "Glasses Set + 8oz", price: 30 },
  p32: { name: "32oz Best Solution", price: 35 },
  p16: { name: "16oz Best Solution", price: 30 },
  p8: { name: "8oz Best Solution", price: 25 },
  p2: { name: "2oz Best Solution", price: 15 },
  c8: { name: "Large C5 (8oz)", price: 30 },
  c2: { name: "Small C5 (2oz)", price: 20 },
};

const TAX_STATE = "WI";
const TAX_PERCENT = "5.5";
const SITE = "https://bestsolutionpolish.com";
const ALLOWED_ORIGINS = [SITE, "https://www.bestsolutionpolish.com"];
const SQUARE = "https://connect.squareup.com";
const SQUARE_VERSION = "2025-01-23";

function cors(origin: string | null) {
  return {
    "Access-Control-Allow-Origin": origin && ALLOWED_ORIGINS.includes(origin) ? origin : SITE,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, authorization, apikey",
    "Vary": "Origin",
  };
}
function reply(body: unknown, status: number, origin: string | null) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors(origin), "Content-Type": "application/json" },
  });
}
const clean = (v: unknown, max: number) => (typeof v === "string" ? v.trim().slice(0, max) : "");

async function square(path: string, token: string, body?: unknown) {
  const res = await fetch(SQUARE + path, {
    method: body ? "POST" : "GET",
    headers: {
      "Authorization": "Bearer " + token,
      "Square-Version": SQUARE_VERSION,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

Deno.serve(async (req) => {
  const origin = req.headers.get("origin");
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
  if (req.method !== "POST") return reply({ error: "POST only" }, 405, origin);

  const token = Deno.env.get("SQUARE_ACCESS_TOKEN");
  if (!token) return reply({ error: "Card checkout is not set up yet." }, 503, origin);

  let input: any;
  try { input = await req.json(); } catch { return reply({ error: "Bad request" }, 400, origin); }

  // Cart -> line items, priced from the table above.
  const items = Array.isArray(input?.items) ? input.items.slice(0, 40) : [];
  const line_items = [];
  for (const it of items) {
    const p = PRICES[String(it?.id)];
    const qty = Math.floor(Number(it?.qty));
    if (!p || !(qty >= 1 && qty <= 99)) return reply({ error: "Unknown item in cart" }, 400, origin);
    line_items.push({
      name: p.name,
      quantity: String(qty),
      base_price_money: { amount: p.price * 100, currency: "USD" },
    });
  }
  if (!line_items.length) return reply({ error: "Cart is empty" }, 400, origin);

  const a = input?.address ?? {};
  const state = clean(a.state, 2).toUpperCase();
  const name = clean(input?.name, 80);
  const street = clean(a.street, 120), apt = clean(a.apt, 60), city = clean(a.city, 80), zip = clean(a.zip, 10);

  let location_id = Deno.env.get("SQUARE_LOCATION_ID") || "";
  if (!location_id) {
    const loc = await square("/v2/locations", token);
    const active = (loc.data?.locations ?? []).find((l: any) => l.status === "ACTIVE");
    if (!active) return reply({ error: "No Square location found" }, 502, origin);
    location_id = active.id;
  }

  const order: any = { location_id, line_items };
  if (state === TAX_STATE) {
    order.taxes = [{ uid: "wi-sales-tax", name: "WI Sales Tax", percentage: TAX_PERCENT, scope: "ORDER" }];
  }

  const shipTo = [name, street + (apt ? ", " + apt : ""), `${city}, ${state} ${zip}`].filter(Boolean).join(" | ");
  const base: any = {
    order,
    checkout_options: {
      redirect_url: SITE + "/?paid=1",
      ask_for_shipping_address: false,
    },
    payment_note: ("Website order. Ship to: " + shipTo).slice(0, 500),
  };

  // Pre-fill what we already know so the customer types as little as possible.
  const pre: any = {};
  const email = clean(input?.email, 120);
  if (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) pre.buyer_email = email;
  const digits = clean(input?.phone, 30).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  if (digits.length === 10) pre.buyer_phone_number = "+1" + digits;
  if (street && city && state && zip) {
    const parts = name.split(/\s+/);
    pre.buyer_address = {
      address_line_1: street,
      ...(apt ? { address_line_2: apt } : {}),
      locality: city,
      administrative_district_level_1: state,
      postal_code: zip,
      country: "US",
      ...(parts[0] ? { first_name: parts[0] } : {}),
      ...(parts.length > 1 ? { last_name: parts.slice(1).join(" ") } : {}),
    };
  }

  let res = await square("/v2/online-checkout/payment-links", token, {
    ...base, idempotency_key: crypto.randomUUID(), pre_populated_data: pre,
  });
  // Square rejects the whole link if it dislikes a pre-filled phone/email. Retry bare.
  if (!res.ok && res.status === 400) {
    res = await square("/v2/online-checkout/payment-links", token, {
      ...base, idempotency_key: crypto.randomUUID(),
    });
  }
  const url = res.data?.payment_link?.url;
  if (!res.ok || !url) {
    console.error("Square error", res.status, JSON.stringify(res.data?.errors ?? res.data));
    return reply({ error: "Could not start card checkout" }, 502, origin);
  }
  return reply({ url }, 200, origin);
});
