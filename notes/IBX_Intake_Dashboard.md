# IBX Intake Dashboard

Admin dashboard for Inner Banks Exchange at https://ibx-intake.web.app (noindex, login required).
Hub that watches and feeds the IBX flagship sites: IBX Shop, IBX Connect (Community Board), Help Wanted board, IBX News Wire.

## Access
- Admin login (email + password), log out link

## Site status sidebar
- IBX Shop: unsold items count, open site
- IBX Connect: new posts, comments, reports counts, open site
- IBX News Wire: active alerts, headlines shown, sources OK (reads ibxconnect.web.app/wire/status.json)
- Sync check

## Quick-jump bar
New posts, Comments, Reports, Unsold items, Quick add (Inventory), Announce (Spotlight)

## Sections
- Post moderation: approve or remove Community Board and Help Wanted posts in place
- Projects: add a project, import from another assistant; private to the login
- Inventory intake form: brand, category, size, price (USD), grade, flaws and work done, photo upload (shrunk and saved with the item) or photo link, Stripe Payment Link, Save to Inventory
  - Categories: Outerwear, Tops, Bottoms, Shoes & Accessories, Lighting, Home Decor, Workshop & Tools, Other
  - Grades: A clean and ready, B honest wear, C priced for the work
  - Stripe tip: limit the Payment Link to one payment to prevent double purchases
- Unsold items: inventory not yet sold, links to IBX Shop
- Community board settings: site-wide toggle to allow comments
- Spotlight: post and pin announcements to the Community Board
- Live community posts: links to Community Board and Help Wanted
- Backup: download inventory, posts, spotlights, comments and reports as one file, monthly
