/**
 * deckgen.js — Universal PowerPoint Deck Generator
 * Usage: node deckgen.js
 * Requires: npm install pptxgenjs
 *
 * HOW TO USE WITH GITHUB COPILOT:
 * 1. Edit the CONFIG section to set your title, theme, and output file
 * 2. Scroll to SLIDES and add/describe your slides using the helper functions
 * 3. Let Copilot autocomplete based on your comments
 * 4. Run: node deckgen.js
 */

const pptxgen = require("pptxgenjs");

// ─────────────────────────────────────────────
// CONFIG — Edit this section
// ─────────────────────────────────────────────
const CONFIG = {
  title: "Presentation Title",
  subtitle: "Subtitle or tagline",
  author: "Your Name",
  date: new Date().toLocaleDateString("en-US", { year: "numeric", month: "long" }),
  outputFile: "deck.pptx",

  // Color theme — change these to match your brand/topic
  // Rule: NO '#' prefix in hex colors (required by pptxgenjs)
  colors: {
    primary:    "1E2761",   // Dark navy — used for title/closing slide backgrounds
    secondary:  "CADCFC",  // Ice blue — card backgrounds, accents
    accent:     "F96167",  // Coral — highlights, callouts
    dark:       "1A1A2E",  // Near black — dark text
    muted:      "64748B",  // Muted slate — captions, labels
    white:      "FFFFFF",
    light:      "F8F9FA",  // Off-white — content slide backgrounds
    border:     "E2E8F0",  // Light border
  },

  // Font pairing
  fonts: {
    heading: "Georgia",     // Slide titles
    body:    "Calibri",     // Body text, bullets
  },
};

const C = CONFIG.colors;
const F = CONFIG.fonts;

// ─────────────────────────────────────────────
// HELPERS — Reusable slide builders
// ─────────────────────────────────────────────

// Always use factory functions for shadow — pptxgenjs mutates objects in-place
const makeShadow = (opacity = 0.15) => ({
  type: "outer", color: "000000", blur: 8, offset: 3, angle: 135, opacity
});

/**
 * TITLE SLIDE — Dark background, centered title + subtitle
 */
function titleSlide(pres, { title, subtitle, eyebrow, author, date } = {}) {
  const s = pres.addSlide();
  s.background = { color: C.primary };

  // Accent bar top
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.accent }, line: { color: C.accent }
  });

  // Eyebrow label (optional)
  if (eyebrow) {
    s.addText(eyebrow.toUpperCase(), {
      x: 0.5, y: 1.4, w: 9, h: 0.3,
      fontFace: F.body, fontSize: 11, color: C.secondary,
      charSpacing: 4, align: "center"
    });
  }

  // Main title
  s.addText(title || CONFIG.title, {
    x: 0.5, y: eyebrow ? 1.7 : 1.5, w: 9, h: 1.4,
    fontFace: F.heading, fontSize: 44, bold: true,
    color: C.white, align: "center"
  });

  // Subtitle
  s.addText(subtitle || CONFIG.subtitle, {
    x: 0.5, y: 3.2, w: 9, h: 0.6,
    fontFace: F.body, fontSize: 18, color: C.secondary, align: "center"
  });

  // Author / date
  const byline = [author || CONFIG.author, date || CONFIG.date].filter(Boolean).join("  ·  ");
  s.addText(byline, {
    x: 0.5, y: 5.0, w: 9, h: 0.35,
    fontFace: F.body, fontSize: 11, color: C.muted, align: "center"
  });

  return s;
}

/**
 * SECTION DIVIDER — Dark background, bold section header
 */
function sectionSlide(pres, { title, subtitle } = {}) {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.accent }, line: { color: C.accent }
  });

  s.addText(title, {
    x: 0.5, y: 1.8, w: 9, h: 1.2,
    fontFace: F.heading, fontSize: 40, bold: true, color: C.white
  });

  if (subtitle) {
    s.addText(subtitle, {
      x: 0.5, y: 3.1, w: 8, h: 0.6,
      fontFace: F.body, fontSize: 16, color: C.secondary
    });
  }

  return s;
}

/**
 * CONTENT SLIDE — Title bar + body area. Pass children to fill the body.
 * Call addContent(s, ...) helpers after this to populate.
 */
function contentSlide(pres, { title, subtitle } = {}) {
  const s = pres.addSlide();
  s.background = { color: C.light };

  // Title bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.primary }, line: { color: C.primary }
  });

  s.addText(title, {
    x: 0.5, y: 0, w: 9, h: 1.1, margin: 0,
    fontFace: F.heading, fontSize: 28, bold: true, color: C.white, valign: "middle"
  });

  if (subtitle) {
    s.addText(subtitle, {
      x: 0.5, y: 1.15, w: 9, h: 0.35,
      fontFace: F.body, fontSize: 12, color: C.muted
    });
  }

  return s;
}

/**
 * TWO-COLUMN SLIDE — Left text/bullets, right content area
 * Returns { slide, leftX, leftY, leftW, rightX, rightY, rightW, bodyH }
 * so you can position content in each column
 */
function twoColumnSlide(pres, { title, subtitle } = {}) {
  const s = contentSlide(pres, { title, subtitle });
  const top = subtitle ? 1.6 : 1.25;
  return {
    slide: s,
    leftX: 0.4, leftY: top, leftW: 4.6,
    rightX: 5.2, rightY: top, rightW: 4.4,
    bodyH: 3.8,
  };
}

/**
 * Add a bullet list to a slide
 */
function addBullets(slide, items, { x, y, w, h, fontSize = 15, indent = false } = {}) {
  const textArray = items.map((item, i) => ({
    text: item,
    options: {
      bullet: true,
      indentLevel: indent ? 1 : 0,
      breakLine: i < items.length - 1,
      fontSize,
      fontFace: F.body,
      color: C.dark,
      paraSpaceAfter: 6,
    }
  }));
  slide.addText(textArray, { x, y, w, h: h || 3.5, valign: "top" });
}

/**
 * Add a colored card (rectangle + text) to a slide
 */
function addCard(slide, pres, { x, y, w, h, bgColor, text, subtext, textColor = "FFFFFF", icon } = {}) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: bgColor || C.primary },
    shadow: makeShadow(0.12),
    line: { color: bgColor || C.primary },
  });

  const textItems = [{ text, options: { bold: true, breakLine: true, fontSize: 14, fontFace: F.heading } }];
  if (subtext) textItems.push({ text: subtext, options: { fontSize: 12, fontFace: F.body } });

  slide.addText(textItems, {
    x: x + 0.15, y, w: w - 0.3, h,
    color: textColor, valign: "middle"
  });
}

/**
 * Add a stat callout (big number + label) to a slide
 */
function addStat(slide, pres, { x, y, w, h, value, label, color } = {}) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: color || C.primary },
    shadow: makeShadow(0.12),
    line: { color: color || C.primary },
  });

  slide.addText(value, {
    x, y: y + 0.1, w, h: h * 0.55,
    fontFace: F.heading, fontSize: 52, bold: true,
    color: C.white, align: "center", valign: "bottom"
  });

  slide.addText(label, {
    x, y: y + h * 0.6, w, h: h * 0.35,
    fontFace: F.body, fontSize: 12,
    color: C.secondary, align: "center", valign: "top"
  });
}

/**
 * Add a styled table to a slide
 */
function addTable(slide, { headers, rows, x = 0.4, y = 1.25, w = 9.2 } = {}) {
  const colW = headers.map(() => w / headers.length);

  const tableData = [
    // Header row
    headers.map(h => ({
      text: h,
      options: {
        bold: true, color: C.white,
        fill: { color: C.primary },
        align: "center", valign: "middle",
        fontFace: F.body, fontSize: 13,
        margin: [6, 8, 6, 8],
      }
    })),
    // Data rows
    ...rows.map((row, ri) =>
      row.map(cell => ({
        text: cell || "",
        options: {
          fill: { color: ri % 2 === 0 ? C.white : "F1F5F9" },
          color: C.dark, fontFace: F.body, fontSize: 12,
          margin: [5, 8, 5, 8],
        }
      }))
    )
  ];

  slide.addTable(tableData, {
    x, y, w,
    colW,
    border: { pt: 0.5, color: C.border },
  });
}

/**
 * CLOSING SLIDE — Dark background, CTA or summary
 */
function closingSlide(pres, { headline, subtext, contact } = {}) {
  const s = pres.addSlide();
  s.background = { color: C.primary };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.accent }, line: { color: C.accent }
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: C.accent }, line: { color: C.accent }
  });

  s.addText(headline || "Thank You", {
    x: 0.5, y: 1.5, w: 9, h: 1.5,
    fontFace: F.heading, fontSize: 48, bold: true, color: C.white, align: "center"
  });

  if (subtext) {
    s.addText(subtext, {
      x: 0.5, y: 3.1, w: 9, h: 0.7,
      fontFace: F.body, fontSize: 18, color: C.secondary, align: "center"
    });
  }

  if (contact) {
    s.addText(contact, {
      x: 0.5, y: 4.8, w: 9, h: 0.4,
      fontFace: F.body, fontSize: 12, color: C.muted, align: "center"
    });
  }

  return s;
}

// ─────────────────────────────────────────────
// SLIDES — Build your deck here
// ─────────────────────────────────────────────
// Copilot Tip: Describe each slide as a comment, then let Copilot fill in the helper calls
// Example: // Slide 3: Two-column layout — left bullets on process, right stat cards

async function buildDeck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = CONFIG.author;
  pres.title = CONFIG.title;

  // ── SLIDE 1: Title ──────────────────────────────────────────────────────────
  titleSlide(pres, {
    title: CONFIG.title,
    subtitle: CONFIG.subtitle,
    eyebrow: "Quarterly Business Review",
  });

  // ── SLIDE 2: Agenda ─────────────────────────────────────────────────────────
  const agenda = contentSlide(pres, { title: "Agenda" });
  addBullets(agenda, [
    "Overview & Background",
    "Key Results and Metrics",
    "Risks and Mitigations",
    "Recommendations",
    "Next Steps",
  ], { x: 0.8, y: 1.4, w: 8.4, h: 3.8, fontSize: 17 });

  // ── SLIDE 3: Stats / Metrics ─────────────────────────────────────────────────
  const metrics = contentSlide(pres, { title: "Key Metrics", subtitle: "Year-to-date performance" });
  addStat(metrics, pres, { x: 0.3, y: 1.6, w: 2.1, h: 2.4, value: "94%",  label: "Customer Satisfaction", color: C.primary });
  addStat(metrics, pres, { x: 2.6, y: 1.6, w: 2.1, h: 2.4, value: "$2.4M", label: "Revenue Generated",    color: "028090" });
  addStat(metrics, pres, { x: 4.9, y: 1.6, w: 2.1, h: 2.4, value: "12",   label: "Projects Delivered",   color: "F96167" });
  addStat(metrics, pres, { x: 7.2, y: 1.6, w: 2.1, h: 2.4, value: "3.2x", label: "ROI",                  color: "1E2761" });

  // ── SLIDE 4: Two-column content ──────────────────────────────────────────────
  const { slide: col2, leftX, leftY, leftW, rightX, rightY, rightW, bodyH } = twoColumnSlide(pres, {
    title: "Findings & Analysis",
    subtitle: "Summary of key observations",
  });

  addBullets(col2, [
    "Customer acquisition cost decreased 18% YoY",
    "Engagement on digital channels up 42%",
    "Support ticket volume reduced by 30%",
    "Team velocity increased across all squads",
  ], { x: leftX, y: leftY, w: leftW, h: bodyH - 0.2 });

  addCard(col2, pres, {
    x: rightX, y: rightY, w: rightW, h: 1.1,
    bgColor: C.primary, text: "Top Performing Region", subtext: "APAC · +68% growth"
  });
  addCard(col2, pres, {
    x: rightX, y: rightY + 1.25, w: rightW, h: 1.1,
    bgColor: "028090", text: "Product of the Quarter", subtext: "Platform v3 · 4,200 users"
  });
  addCard(col2, pres, {
    x: rightX, y: rightY + 2.5, w: rightW, h: 1.1,
    bgColor: "F96167", text: "Risk to Watch", subtext: "Vendor contract renewal · Q3"
  });

  // ── SLIDE 5: Table ───────────────────────────────────────────────────────────
  const tableSlide = contentSlide(pres, { title: "Project Status" });
  addTable(tableSlide, {
    headers: ["Project", "Owner", "Status", "Due Date", "Budget"],
    rows: [
      ["Platform Redesign", "Alex Kim",    "In Progress", "Jun 2025", "On Track"],
      ["Data Migration",    "Sam Rivera",  "Pending",     "Jul 2025", "At Risk"],
      ["API Integration",   "Jordan Lee",  "Complete",    "Apr 2025", "Delivered"],
      ["Security Audit",    "Taylor Moss", "In Progress", "May 2025", "On Track"],
    ],
    y: 1.3,
  });

  // ── SLIDE 6: Recommendations ─────────────────────────────────────────────────
  const recs = contentSlide(pres, { title: "Recommendations" });
  const recItems = [
    { num: "01", title: "Accelerate platform rollout", desc: "Prioritize Q3 release to capture market window" },
    { num: "02", title: "Increase support capacity",   desc: "Hire 2 additional engineers before Q3 peak" },
    { num: "03", title: "Renegotiate vendor contract",  desc: "Start renewal discussions now to avoid Q3 disruption" },
  ];

  recItems.forEach(({ num, title, desc }, i) => {
    const y = 1.3 + i * 1.3;
    recs.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y, w: 9.2, h: 1.1,
      fill: { color: C.white }, shadow: makeShadow(0.08), line: { color: C.border }
    });
    recs.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y, w: 0.6, h: 1.1,
      fill: { color: C.primary }, line: { color: C.primary }
    });
    recs.addText(num, {
      x: 0.4, y, w: 0.6, h: 1.1, margin: 0,
      fontFace: F.heading, fontSize: 16, bold: true, color: C.white,
      align: "center", valign: "middle"
    });
    recs.addText([
      { text: title, options: { bold: true, breakLine: true, fontSize: 14, fontFace: F.heading, color: C.dark } },
      { text: desc,  options: { fontSize: 12, fontFace: F.body, color: C.muted } }
    ], { x: 1.2, y: y + 0.05, w: 8.2, h: 1.0, valign: "middle" });
  });

  // ── SLIDE 7: Closing ─────────────────────────────────────────────────────────
  closingSlide(pres, {
    headline: "Questions?",
    subtext: "Let's discuss next steps",
    contact: CONFIG.author + "  ·  " + CONFIG.date,
  });

  // ── WRITE FILE ───────────────────────────────────────────────────────────────
  await pres.writeFile({ fileName: CONFIG.outputFile });
  console.log(`✅ Created: ${CONFIG.outputFile}`);
}

buildDeck().catch(console.error);
