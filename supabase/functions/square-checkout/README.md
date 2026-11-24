# Square exact-amount card checkout

**What it does:** when a customer picks Credit / Debit Card and taps the gold button,
the site sends the cart here, this builds a Square payment link for the exact order
(with WI sales tax when it ships to Wisconsin), and the customer lands on Square's
secure page with the total already filled in. No typing an amount. No waiting on a text.

**Status: deployed and wired to the site.** It runs on the Supabase project
`froggy-money` as the Edge Function `square-checkout` (Verify JWT off), and
`CHECKOUT_API` in `index.html` points at it. It does nothing until the Square token
is added. Until then, and any time it errors, card orders use the older flow.

## The one step left

1. **Square token.** developer.squareup.com > Apps > create an app (any name) >
   Credentials > **Production** > copy the Access token.
2. **Add the secret** in Supabase > Edge Functions > Secrets:
   `SQUARE_ACCESS_TOKEN` = that token. Never paste it into a file or a chat.
3. **Test it** with a real small card order on the site, then refund it in Square.

To change the function, edit `index.ts` and redeploy it under the same name.

## Keep in step

Prices are repeated in `index.ts` (the `PRICES` table) so a customer cannot change a
price from their browser. **Change a price in `index.html`, change it here too**, then
redeploy.

If the function is down or errors, the site falls back to the older card flow on its
own, so an order is never lost.
