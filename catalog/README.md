# Ricciocaprese Jordan — Interactive 3D Catalogue

A one-page product catalogue for **Ricciocaprese Jordan**. Customers can turn every piece around in 3D, change its glaze colour and pick a size before ordering.

It's based on an Instagram reel showing "an interactive catalogue with a 3D view of the products, made with Claude", rebuilt for [ricciocapresejo.com](https://www.ricciocapresejo.com).

- **File:** `catalog/index.html` (a single file with no build step)
- **Branch:** `claude/inspiring-knuth-w464xu`

---

## 1. What I took from the website

| Item | Value |
|---|---|
| Main colour (navy) | `#17456F` |
| Light blue | `#A8C8E9` |
| Background (cream) | `#F7F3EC` / `#FCFCFC` |
| Text | `#1B2328` |
| Heading font | Cormorant Garamond |
| Body font | Inter |
| Tagline | "Capri, in porcelain." |
| Currency | JOD |
| Stock labels | In stock · Last pieces · Sold out |

I also took **all 46 products**: names, sizes, prices, stock status and the real product photos. They're grouped the same way as on the site:

Riccio · Lady Capri · Dalia · Anemone · New Fragrance · Fiori di Capri · Tulipano · Regina · Fontelina · Lighting · Scent Diffusers · Refills · Decor

There are also **27 glaze colours**, using the colour names from the site's filter (Azzurro Capri, Blu Capri, Rosso, Corallo, Ciclamino, Verde Ramino…).

---

## 2. What the page does

### Hero
- The logo, the "RICCIOCAPRESE" wordmark and the tagline "Capri, in porcelain — now in 3D."
- A large porcelain **sea urchin in 3D**. You can drag it to spin, and it slowly changes colour through the brand glazes.

### Catalogue
- A toolbar that stays at the top: **category filters** (All, Diffusers, Decor, Lighting, Refills), **search**, and a **cart counter**.
- Product cards show the photo, a "3D" badge, the name, size, colour strip, price and stock status.

### 3D viewer (opens when you tap a product)
- **Drag to rotate, scroll or pinch to zoom.** It rotates by itself until you touch it.
- Buttons for **auto-rotate**, **reset view** and **close-up**.
- **Glaze picker:** the 3D model's colour changes as soon as you tap a colour.
- **Size picker:** M8 / M12 / M18 and so on. Sold-out sizes are crossed out.
- Price, an **Add to cart** button, and a delivery note ("arranged with you on WhatsApp").
- Every product has its own link (for example `index.html#riccio-0`), so you can share a product directly.

### Works on phones
- On phones, the 3D model sits on top and the details go below.
- Tested at desktop width (1280 px) and on an iPhone 13. There's no sideways scrolling.

---

## 3. The 3D models

Each design is **built in code** with Three.js, so no 3D files are needed:

| Product | How it's modelled |
|---|---|
| Riccio | Round porcelain urchin with short rounded spines on a glass diffuser with reeds |
| Lady Capri | A taller, slimmer urchin |
| Regina | An urchin with longer, bolder spines |
| Dalia | Layers of cupped petals, like a dahlia |
| Anemone | A cluster of tapering tentacles |
| New Fragrance / Decor Riccio | A low half-dome covered in fine spines |
| Fiori di Capri | 1–3 porcelain lilies in a clear block |
| Tulipano | A six-petal tulip on a diffuser |
| Lighting (Lume) | A Riccio or Dalia shade on a base, glowing warm from inside |
| Fontelina | 1950s-style striped porcelain (one colour, white or blue) |
| Pigna | A pine cone made of stacked scales |
| Ramocaprese | Branching coral on a round base |
| Candeliere Foglia | A leaf candle holder with a flickering flame |
| Refills / Scent Diffuser | Glass bottles with liquid inside |

The porcelain uses a glossy, clear-coated material, and the bottles are see-through glass with fragrance inside. Every model sits on a soft shadow.

---

## 4. Tech used

- **HTML + CSS + JavaScript** in one file
- **Three.js 0.160** (loaded from the jsDelivr CDN) with OrbitControls, RoomEnvironment lighting and RoundedBoxGeometry
- **Google Fonts:** Cormorant Garamond and Inter
- Product photos load from `ricciocapresejo.com/img/…`

---

## 5. How to edit it

Everything is at the top of the script in `index.html`:

- **`GROUPS`**: each collection with its name, tagline, description and items.
  Each item is `[size, variant, price, stock, imageId]`, where stock is `"in"`, `"low"` or `"out"`.
- **`COLOURS`**: glaze names and their hex colours.
- **`SIZE_SCALE`**: how big each size looks in 3D.

Example: to mark Riccio M18 as back in stock, change `"out"` to `"in"` on its line.

---

## 6. How to view it

- **Locally:** open `catalog/index.html` in Chrome or Safari (it needs internet for the 3D library and photos).
- **Online:** turn on **GitHub Pages** for the repo. The page will then be at `…github.io/test/catalog/`.

---

## 7. Limits and next steps

- The 3D shapes are **close illustrations**, not scans. For exact models, scan each piece with **Polycam** or **Luma AI** and swap the `.glb` files in.
- The glaze hex colours are **my estimates** from the colour names. Replace them with the real ones.
- The cart is a **demo only**. It isn't connected to the real checkout yet.

Ideas for next steps:
1. Send orders to WhatsApp with the chosen colour and size
2. An Arabic version that reads right to left
3. A "View in your room" (AR) button on phones
4. A "View in 3D" button on the main website
