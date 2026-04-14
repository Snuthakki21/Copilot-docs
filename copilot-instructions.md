# GitHub Copilot Instructions – Word Document Generation

When asked to generate a Word document, report, proposal, meeting notes, or any `.docx` file:

## Always Use the `docx` npm Library

```bash
npm install docx
# or globally: npm install -g docx
```

Generate documents with Node.js (`node docgen.js`), NOT python-docx.

---

## Document Structure Rules

### Page Setup (US Letter, 1-inch margins)
```javascript
sections: [{
  properties: {
    page: {
      size: { width: 12240, height: 15840 }, // US Letter in DXA
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch
    }
  },
  children: [/* content */]
}]
```

### Font & Styles
- Default font: **Arial 12pt**
- H1: Arial 16pt bold, H2: Arial 14pt bold, H3: Arial 12pt bold
- Always override built-in styles using IDs "Heading1", "Heading2", "Heading3"
- Include `outlineLevel` on headings (0 for H1, 1 for H2, etc.) for TOC support

### Lists — NEVER use unicode bullets
```javascript
// WRONG:
new Paragraph({ children: [new TextRun("• Item")] })

// CORRECT — define numbering config, then reference it:
numbering: {
  config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ]
}
// Usage:
new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("Item")] })
```

### Tables — Dual widths required
```javascript
// Always set width on BOTH the table AND each cell (must match columnWidths)
// Always use WidthType.DXA (never PERCENTAGE — breaks in Google Docs)
// Always use ShadingType.CLEAR (not SOLID — prevents black backgrounds)
// Content width for US Letter with 1" margins = 9360 DXA

new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3120, 3120, 3120], // Must sum to table width
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 3120, type: WidthType.DXA },
          shading: { fill: "2E4057", type: ShadingType.CLEAR }, // Header row color
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: "Column", bold: true, color: "FFFFFF" })] })]
        })
      ]
    })
  ]
})
```

### Page Breaks
```javascript
// MUST be inside a Paragraph (not standalone)
new Paragraph({ children: [new PageBreak()] })
```

### Headers & Footers with Page Numbers
```javascript
headers: {
  default: new Header({ children: [new Paragraph({ children: [new TextRun("Document Title")] })] })
},
footers: {
  default: new Footer({ children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
  })] })
}
```

---

## Common Document Templates

### Report / Status Update
Sections: Title, Date/Author, Executive Summary, Status Table (Task | Owner | Status | Due Date), Key Risks, Next Steps

### Proposal / Spec
Sections: Title, Overview, Background, Objectives, Proposed Solution, Timeline, Risks & Mitigations, Appendix

### Meeting Notes
Sections: Meeting Title, Date/Time/Attendees, Agenda, Discussion Points, Decisions Made, Action Items Table (Item | Owner | Due Date)

---

## Critical Rules
- **Never use `\n` inside TextRun** — use separate Paragraph elements
- **Always explicitly set page size** — docx defaults to A4
- **Table width must equal sum of columnWidths** exactly
- **Cell `margins` are internal padding** — they reduce content area, not add to width
- **PageBreak must be inside a Paragraph**
- **ImageRun requires a `type` field** (e.g., `type: "png"`)
- **Use `outlineLevel`** on heading paragraphs for Table of Contents support
