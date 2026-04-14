/**
 * docgen.js — Universal Word Document Generator
 * Usage: node docgen.js
 * Requires: npm install docx
 *
 * HOW TO USE WITH GITHUB COPILOT:
 * 1. Edit the DOCUMENT CONFIG section below to describe your document
 * 2. Let Copilot autocomplete the `sections` content
 * 3. Run: node docgen.js
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, LevelFormat, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak, ImageRun,
  ExternalHyperlink, TableOfContents
} = require("docx");
const fs = require("fs");

// ─────────────────────────────────────────────
// DOCUMENT CONFIG — Edit this section
// ─────────────────────────────────────────────
const CONFIG = {
  title: "Document Title",
  subtitle: "Subtitle or Description",
  author: "Your Name",
  date: new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }),
  outputFile: "output.docx",
  // type: "report" | "proposal" | "meeting-notes" | "general"
  type: "general",
};

// ─────────────────────────────────────────────
// HELPERS — Reusable building blocks
// ─────────────────────────────────────────────

/** Heading paragraph */
function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] });
}

/** Body paragraph */
function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    spacing: { after: 120 },
    children: [new TextRun({ text, bold: opts.bold, italic: opts.italic, size: opts.size })],
  });
}

/** Empty spacer line */
function spacer() {
  return new Paragraph({ children: [new TextRun("")] });
}

/** Horizontal rule (bottom border on an empty paragraph) */
function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 1 } },
    children: [new TextRun("")],
  });
}

/** Bullet list item */
function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    children: [new TextRun(text)],
  });
}

/** Numbered list item */
function numbered(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "numbers", level },
    children: [new TextRun(text)],
  });
}

/** Page break */
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

/**
 * Table builder
 * @param {string[]} headers - Column header labels
 * @param {string[][]} rows - Array of row arrays
 * @param {object} opts - { headerColor: hex, columnWidths: number[] }
 */
function table(headers, rows, opts = {}) {
  const headerColor = opts.headerColor || "2E4057";
  const totalWidth = 9360; // US Letter content width in DXA
  const colCount = headers.length;
  const colWidths = opts.columnWidths || headers.map(() => Math.floor(totalWidth / colCount));
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

  const headerRow = new TableRow({
    children: headers.map((h, i) =>
      new TableCell({
        borders,
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: headerColor, type: ShadingType.CLEAR },
        margins: cellMargins,
        children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF" })] })],
      })
    ),
  });

  const dataRows = rows.map((row) =>
    new TableRow({
      children: row.map((cell, i) =>
        new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          margins: cellMargins,
          children: [new Paragraph({ children: [new TextRun(cell || "")] })],
        })
      ),
    })
  );

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

// ─────────────────────────────────────────────
// DOCUMENT CONTENT — Add your content here
// ─────────────────────────────────────────────
// Copilot Tip: Describe what you want below as a comment and let Copilot fill it in
// Example: // Status report for Q1 2025 with project table and risks section

const content = [
  // Title block
  p(CONFIG.title, { bold: true, size: 40, center: true }),
  p(CONFIG.subtitle, { size: 24, center: true }),
  p(`${CONFIG.author}  ·  ${CONFIG.date}`, { center: true }),
  spacer(),
  divider(),
  spacer(),

  // ── ADD YOUR CONTENT BELOW ──
  // Copilot will autocomplete based on CONFIG.type and your comments

  h1("Executive Summary"),
  p("Provide a brief overview of the key points, findings, or purpose of this document."),
  spacer(),

  h1("Details"),
  h2("Section One"),
  p("Add your content here."),
  bullet("Key point one"),
  bullet("Key point two"),
  bullet("Key point three"),
  spacer(),

  h2("Section Two"),
  p("Add your content here."),
  table(
    ["Item", "Owner", "Status", "Due Date"],
    [
      ["Task 1", "John Doe", "In Progress", "2025-05-01"],
      ["Task 2", "Jane Smith", "Pending", "2025-05-15"],
      ["Task 3", "Team", "Complete", "2025-04-30"],
    ]
  ),
  spacer(),

  h1("Next Steps"),
  numbered("First action item"),
  numbered("Second action item"),
  numbered("Third action item"),
];

// ─────────────────────────────────────────────
// BUILD & SAVE
// ─────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }, {
          level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }, // 12pt
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "2E4057" },
        paragraph: { spacing: { before: 300, after: 180 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "445566" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // US Letter
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1 inch
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
              children: [new TextRun({ text: CONFIG.title, color: "888888", size: 18 })],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
              children: [
                new TextRun({ text: `${CONFIG.author}  ·  `, color: "888888", size: 18 }),
                new TextRun({ children: [PageNumber.CURRENT], color: "888888", size: 18 }),
              ],
            }),
          ],
        }),
      },
      children: content,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(CONFIG.outputFile, buffer);
  console.log(`✅ Created: ${CONFIG.outputFile}`);
});
