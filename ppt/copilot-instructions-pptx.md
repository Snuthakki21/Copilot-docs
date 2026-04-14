# GitHub Copilot Instructions – PowerPoint Deck Generation

When asked to generate a PowerPoint, slide deck, or `.pptx` file:

## Always Use the `pptxgenjs` npm Library

```bash
npm install pptxgenjs
# or globally: npm install -g pptxgenjs
```

Generate decks with Node.js (`node deckgen.js`), NOT python-pptx.

---

## Critical Rules (Violations Corrupt Files or Break Output)

### 1. NEVER use `#` in hex colors
```javascript
color: "FF0000"      // ✅ CORRECT
color: "#FF0000"     // ❌ CORRUPTS FILE
```

### 2. NEVER encode opacity in hex (8-char hex corrupts files)
```javascript
shadow: { color: "00000020" }                          // ❌ CORRUPTS FILE
shadow: { color: "000000", opacity: 0.12 }             // ✅ CORRECT
```

### 3. NEVER share option objects across multiple calls (pptxgenjs mutates in-place)
```javascript
// ❌ WRONG - mutated after first use
const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
slide.addShape(pres.shapes.RECTANGLE, { shadow });
slide.addShape(pres.shapes.RECTANGLE, { shadow }); // Already mutated — corrupt

// ✅ CORRECT - fresh object each time
const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow() });
slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow() });
```

### 4. NEVER use unicode bullet characters
```javascript
slide.addText("• Item", {...});  // ❌ Creates double-bullets

// ✅ CORRECT
slide.addText([
  { text: "Item 1", options: { bullet: true, breakLine: true } },
  { text: "Item 2", options: { bullet: true } }
], { x: 0.5, y: 1, w: 9, h: 3 });
```

### 5. Use `breakLine: true` for multi-line text arrays
```javascript
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2" }
], { x: 0.5, y: 0.5, w: 9, h: 2 });
```

### 6. NEVER use accent lines under titles
Use whitespace or background color for separation — accent underlines are a hallmark of bad AI slides.

---

## Layout & Dimensions

- Always use `LAYOUT_16x9` (10" × 5.625" slide)
- All coordinates/sizes are in inches
- Minimum 0.5" margins from slide edges
- Leave breathing room — never fill every inch

---

## Design Principles

### Color: Pick a real palette (don't default to generic blue)
Commit to one dominant color (60-70% weight), one secondary, one accent. Match the topic.

Example palettes:
| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Executive | `1E2761` | `CADCFC` | `FFFFFF` |
| Energy | `F96167` | `2F3C7E` | `F9E795` |
| Teal Trust | `028090` | `00A896` | `F5F5F5` |
| Charcoal | `36454F` | `F2F2F2` | `212121` |

### Slide structure: Dark/light sandwich
- Title slide: dark background
- Content slides: light background
- Closing slide: dark background

### Every slide needs a visual element
Never text-only. Add a shape, colored card, icon circle, stat callout, or table.

### Vary layouts across slides — avoid repeating the same template
Use: two-column, icon+text rows, stat callouts, table, image+content, etc.

### Typography
- Titles: 36-44pt bold, heading font (e.g., Georgia, Trebuchet MS, Arial Black)
- Body: 14-16pt, clean font (e.g., Calibri, Arial)
- Captions/labels: 10-12pt, muted color

---

## Slide Types to Use

### Title Slide
Dark background, centered title (44pt bold), subtitle (18-20pt), optional divider shape.

### Content Slide (Two-Column)
Left: text/bullets. Right: image, icon grid, or visual. Split roughly 55%/45%.

### Stat Callout Slide
3-4 large numbers (60-72pt bold) with small label text below each. Use colored accent cards.

### Table Slide
Use `addTable()` with header row colored to match palette. Clean borders, comfortable padding.

### Timeline / Process Slide
Numbered steps with connected shapes or progress bar.

### Closing Slide
Dark background matching title slide. Strong call-to-action or summary line.

---

## Charts: Make Them Modern

```javascript
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1, w: 9, h: 4,
  chartColors: ["0D9488", "14B8A6"],     // Match your palette
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showValue: true,
  dataLabelColor: "1E293B",
  showLegend: false,
});
```

---

## Quick Reference
- Slide size: 10" × 5.625" (LAYOUT_16x9)
- No `#` in colors
- No shared option objects
- `bullet: true` not "•"
- `breakLine: true` in text arrays
- Always call `pres.writeFile({ fileName: "deck.pptx" })`
