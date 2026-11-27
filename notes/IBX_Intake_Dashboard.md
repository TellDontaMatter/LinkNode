# IBX Intake Dashboard

Admin dashboard for Inner Banks Exchange at https://ibx-intake.web.app (also ibx-intake.netlify.app).
Code: repo TellDontaMatter/InnerBanksExchange, folder intake/. Plain HTML, no build step.
Backend: Firebase project thruket-site1 (Firestore + Firebase Auth email/password).
Hosting targets in that one Firebase project: ibx-intake, ibxconnect, ibxshop, ibxhelp.

## Built-in projects (default project list)
- IBX Connect: community board, ibxconnect.web.app
- IBX Shop: storefront, ibxshop.web.app
- IBX Help: help wanted and services offered, ibxhelp.web.app
- Suffsa: learning app, suffsa.netlify.app
- Route | Philc: PCS move planner, movebyphilc.netlify.app
- S.E.E. Engine: decision evaluation, seeyouryou.web.app
- City Pay: unit-price lookup (Grok bot), city-pay.pages.dev
Project list syncs across devices through Firestore dashboard/projects, with localStorage fallback.
Projects can be added, removed, or imported from another assistant.

## Flagship check
Pings IBX Shop and IBX Connect, shows whether both answered. Counts refresh every 20 seconds.
Shows auto-approved posts today out of the daily cap of 20.

## Site status sidebar (live site only, not yet in the repo)
- IBX News Wire: active alerts, headlines shown, sources OK, reads ibxconnect.web.app/wire/status.json

## Inventory
- Intake form writes Firestore inventoryItems: brand, category, size, price, grade, flaws, photo_url, payment_link, sold, created_at
- Categories: Outerwear, Tops, Bottoms, Shoes & Accessories, Lighting, Home Decor, Workshop & Tools, Other
- Grades: A clean and ready, B honest wear, C priced for the work
- Photos shrunk on the device and stored inside the item as a data URL; no Firebase Storage bucket
- Stripe Payment Link pasted by hand, one payment per link
- Unsold items: Mark Sold, Fix photo
- IBX Shop reads inventoryItems where sold is false

## Moderation
- Posts (Firestore posts): approve or delete pending posts, remove live posts
- Post categories: jobs, events, kids, services, requests; county tags for the Inner Banks counties and Region-wide
- Auto-approve guardrails: events, kids and requests posts can go live without review if the text passes the spam, link and profanity checks, the contact is a real email or phone, and the daily cap of 20 is not reached
- Comments (Firestore comments): approve or delete; site-wide comments switch in settings/site
- Reports (Firestore reports): neighbors report a post; admin can remove the post and clear the report
- Spotlights (Firestore spotlights): post, pin and remove announcements on the Community Board

## Backup
Download inventory, posts, spotlights, comments and reports as one file, monthly.

## Security
Firestore rules: only the admin email can write inventory, settings, spotlights, the dashboard, or approve and delete.
