# Best Solution — Reorder Page

A single-file customer reorder page for **Best Solution** polish & C5 lotion
(Dot Dynasty LLC). Text the link to customers between shows. They pick bundles,
choose how they want to pay, and submit. Justin gets the order by email, then
confirms shipping and collects payment manually.

## Go live (5 minutes, free)

1. Create a GitHub repo named **`bestsolution`**.
2. Upload `index.html` (and optionally `banner.png` for the link preview image).
3. Repo **Settings → Pages → Deploy from branch → main / root → Save**.
4. Live at: `https://jfgreco84.github.io/bestsolution`

## Connect the order email (REQUIRED — one line)

Orders won't reach Justin until the Formspree form ID is set.

1. At **formspree.io**, create a form with recipient `bestsolutionpolish@gmail.com`.
2. Copy the endpoint, e.g. `https://formspree.io/f/abcdwxyz`.
3. In `index.html`, near the bottom `<script>`, change:
   ```js
   const FORMSPREE_ID = "YOUR_FORM_ID";
   ```
   to your id (only the part after `/f/`):
   ```js
   const FORMSPREE_ID = "abcdwxyz";
   ```
4. Re-upload `index.html`. Done.

Until then, the order button shows a friendly message and lets the customer
**copy their order** to text to Justin, so nothing is ever lost.

## How payment works

The page is an **order intake form, not a checkout**. The payment buttons
(Square / Venmo / Zelle / Cash App) just tell Justin how the customer wants to
pay. Justin sends the request manually after confirming shipping. No card is
ever charged on the page.

## Prices

All prices are **+ shipping** (quoted by Justin after the order comes in).

**Large C5 (8oz) combos:** 32oz+C5L $55 · 16oz+C5L $50 (Most Popular) · 8oz+C5L $45
**Small C5 (2oz) combos:** 32oz+C5S $45 · 16oz+C5S $40 · 8oz+C5S $35 · 2oz+C5S $25 (Gift/Starter)
**Singles:** 32oz $30 · 16oz $25 · 8oz $20 · 2oz $10 · 8oz C5 $25 · 2oz C5 $15

To change a price, edit the `BUNDLES_LARGE`, `BUNDLES_SMALL`, or `SINGLES`
arrays in the `<script>`.

> C5 is a **fine metal restoration lotion** — never labeled a cloth, wipe, or pad.
