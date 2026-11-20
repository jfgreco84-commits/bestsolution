# Square exact-amount card checkout

**What it does:** when a customer picks Credit / Debit Card and taps the gold button,
the site sends the cart here, this builds a Square payment link for the exact order
(with WI sales tax when it ships to Wisconsin), and the customer lands on Square's
secure page with the total already filled in. No typing an amount. No waiting on a text.

**Status: built, NOT switched on.** It needs a Square access token, and it has not been
run against Square yet. Until it is on, card orders use the older flow.

## Turn it on

1. **Square token.** developer.squareup.com > Apps > create an app (any name) >
   Credentials > **Production** > copy the Access token.
2. **Deploy** this folder as a Supabase Edge Function named `square-checkout`
   with **Verify JWT turned OFF** (the website calls it without a login).
3. **Add the secret** in Supabase > Edge Functions > Secrets:
   `SQUARE_ACCESS_TOKEN` = the token from step 1. Never paste it into a file or a chat.
4. **Paste the function URL** into `index.html`:
   `const CHECKOUT_API = "https://<project>.supabase.co/functions/v1/square-checkout";`
5. **Test it** with a real small order and refund it in Square.

## Keep in step

Prices are repeated in `index.ts` (the `PRICES` table) so a customer cannot change a
price from their browser. **Change a price in `index.html`, change it here too**, then
redeploy.

If the function is down or errors, the site falls back to the older card flow on its
own, so an order is never lost.
