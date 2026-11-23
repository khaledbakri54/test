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

---

# Part 2 — Pop-up Book Catalogue (`catalog/book.html`)

The second version follows the reel's "pop-up book" prompt, adapted for Ricciocaprese. The catalogue is an open hardcover book on a dark walnut table in warm late-afternoon sun. Each piece pops up from the page in 3D and folds back down when the page turns.

## The 5 pages

| # | Piece | Arabic | Finishes (glaze) | Price |
|---|---|---|---|---|
| 01 | RICCIO · M12 | ريتشو | Azzurro Capri · Rosso · Bianco | 100 JOD |
| 02 | LADY CAPRI · M10 | ليدي كابري | Blu Notte · Corallo · Grigio Perla | 115 JOD |
| 03 | DALIA · M12 | داليا | Lilla · Ciclamino · Giallo | 100 JOD |
| 04 | ANEMONE · M12 | أنيموني | Acquamarina · Blu Capri · Bianco | 100 JOD |
| 05 | REGINA · 300 ml | ريجينا | Verde Ramino · Bordeaux · Nero | 140 JOD |

## What's in it

- **Scene:** a walnut table with a clear-coat shine, warm sun from the upper left, and an invisible window frame that throws slanted stripes of light and shadow over the book.
- **The book:** reads right to left. It has a navy linen cover, striped page edges, and pages that curve down into the spine.
  - The **left page** has the piece, a large English title, technical drawings with mm dimensions, the printed finish swatches, and the footer.
  - The **right page** is in Arabic: the name, a description, a spec table, the price in JOD, and a Sadu-style triangle border.
- **Technical drawings:** made from the 3D model itself. It's drawn flat from the front and the side, the outlines are traced as ink lines, and the dimensions come from the model's size.
- **Pop-up:** the piece rises out of the page with a small overshoot and a soft contact shadow under it.
- **Page turn:** "Next" lifts the left page and turns it over to the right. The page bends, with the free edge trailing behind. The old piece folds down while riding the turning page, and the new piece pops up once the page passes the middle.
- **Finishes:** choose from the bottom panel or by tapping the swatches printed on the page. The 3D model, the printed swatch frame, the Arabic spec row and the price all update together.
- **Camera:** an overhead "handheld" view that frames the book automatically in the free space on screen. On phones it shows only the piece page. Tap the piece to zoom in.
- **Controls:**
  - Top-left buttons: Autoplay, 360° spin, Zoom to piece, Reset view.
  - Arrows on each side ("Next" is on the left), plus the page numbers 01–05.
  - Keyboard: ← next, → previous.
- **WhatsApp:** the "اطلب عبر واتساب" button opens WhatsApp with a ready-made order message (piece, finish, price).
- **Autoplay (for filming Reels):** press the button, or add `#autoplay` to the link. The UI hides and the camera moves in close. It cycles the three glazes, zooms back out and turns the page, then loops. Tap anywhere to stop.
- **Owner panel:** open the page with `#admin` at the end of the link (for example `book.html#admin`). You can edit names, titles, the description, dimensions, delivery text, the extra spec, each finish's name and price, and the shop's WhatsApp number. The pages redraw as you type.
  - **Save:** on normal hosting, this saves in the browser on that device only.
  - **Shared saves:** if the page is published as a Claude artifact, saves go to a shared database everyone sees, and only editors see the panel.
  - **Reset:** "Reset to default" needs two taps.

## Tested

I tested it in a headless browser (software rendering):
- Loading and the pop-up
- Turning the page forward and back
- Changing the finish from the panel and from the printed swatch
- Editing a price in the owner panel and seeing it on the printed page
- Saving and reloading
- Starting and stopping autoplay
- Phone layout (iPhone 13 size)

There were no console errors.

## Limits

- The pieces are built in code. They're close to the real designs, but not scans.
- Saving from the owner panel on GitHub Pages only saves on that one device. Shared editing needs it published as a Claude artifact, or a small backend.

---

# Part 3 — Realistic 3D models from Higgsfield

Three pieces in the book now use realistic 3D models instead of code-built shapes: **Riccio, Dalia and Lady Capri**. Anemone and Regina are still code-built.

## How they were made

1. **Reference photos:** imported the real product photos from ricciocapresejo.com into Higgsfield.
2. **Clean studio photos (GPT Image 2.6):** made one photo of each topper on its own, in white glaze on a white background, for all 5 pieces. 0.75 credits each.
3. **3D models (Hunyuan 3D v3, image to 3D, 40k faces):** made from the Riccio, Dalia and Lady Capri photos. 15 credits each.
4. **Compression (gltf-transform):** meshopt geometry, WebP textures at 1536 px, light simplification.
   - Riccio: 10.4 MB → 384 KB
   - Dalia: 12.4 MB → 439 KB
   - Lady Capri: 10.7 MB → 334 KB
5. **Files:** saved in `catalog/models/`.

Credits used: about 49 of 52.

## How they're used in `book.html`

- **One white model per piece.** The page tints it to whichever glaze is selected, so all 27 colours work without a separate model for each colour.
- **Riccio and Dalia:** only the porcelain topper is a Higgsfield model. It sits on the code-built glass bottle, with its liquid and reeds, because image-to-3D can't do see-through glass well.
- **Lady Capri:** the whole piece is one model (a porcelain cube with the urchin on top), plus code-built reeds.
- **Same behaviour as before:** the models pop up, fold and ride the page turn exactly like the code-built pieces.
- **Technical drawings:** now traced from the models' surface normals.
- **Loading:** GLTFLoader with MeshoptDecoder.

**Important:** the models load over http(s) (GitHub Pages or any web host). If you open `book.html` straight from disk (`file://`), the browser blocks the model files, so the page falls back to the code-built pieces automatically.

## Adding Anemone and Regina later

The clean topper photos for both are already made in your Higgsfield account. To convert them:
- Converting both costs about 30 more credits.
- Save the files as `models/anemone.glb` and `models/regina.glb`.
- Add them to `GLB_FILES` in `book.html`.
