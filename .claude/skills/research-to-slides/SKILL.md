---
name: research-to-slides
description: "Research a topic online and generate a well-designed presentation. Triggers when user asks to \"research and make slides about X\", \"create a presentation on X with web research\", or similar research → deck workflows. Use this skill whenever the user wants to gather information from the web and turn it into a .pptx file."
---

# Research-to-Slides Skill

## Overview

Given a topic, this skill:
1. Researches the topic via web searches (multiple angles, multiple queries)
2. Organizes findings into a structured outline
3. Generates a polished .pptx presentation using the pptx skill

---

## Phase 1: Research

### 1a. Understand the Topic

Before searching, clarify with the user (if ambiguous):
- **Scope**: How broad or narrow should the research be?
- **Audience**: Who is this presentation for? (executives, students, general public, etc.)
- **Length**: How many slides? (default: 8-12 for a standard deck)
- **Angle**: Any specific perspective to emphasize?

If the user gave a one-liner with no details, ask 1-2 clarifying questions before searching.

### 1b. Search Strategy

Run **at least 4-6 web searches** with different angles. Cover these dimensions:

| Dimension | Example Queries |
|-----------|----------------|
| **Overview** | "What is X", "X explained", "X guide 2025" |
| **Key facts/data** | "X statistics", "X market size", "X trends 2025" |
| **Depth/analysis** | "X benefits and challenges", "X use cases", "X comparison" |
| **Recent news** | "X latest developments", "X news 2025", "X future outlook" |
| **Controversy/criticism** | "X criticism", "X debate", "X risks" |
| **Practical how-to** | "how to use X", "X best practices", "X tutorial" |

Adapt search queries to the specific topic — don't use these as templates, use them as idea starters.

**Run searches in parallel** (single batch of WebSearch calls) for efficiency.

### 1c. Synthesize Findings

After collecting search results, compile findings into a structured research document:

```
## Research Synthesis: [Topic]

### Key Facts & Statistics
- ...

### Main Themes
1. Theme A — one-line summary
2. Theme B — one-line summary
3. Theme C — one-line summary

### Interesting Nuggets
- Surprising or memorable facts

### Timeline / Context
- Historical context if relevant

### Opposing Viewpoints
- Different perspectives if applicable

### Practical Takeaways
- Actionable insights
```

This synthesis becomes the content source for the slides.

---

## Phase 2: Outline & Structure

### 2a. Design the Slide Deck Structure

Map research to slides. A standard presentation structure:

| Slide | Type | Purpose |
|-------|------|---------|
| 1 | Title | Topic + subtitle + hook |
| 2 | Agenda/Overview | What we'll cover (3-5 items) |
| 3 | Context | Why this matters now, background |
| 4-6 | Core Content | Main themes from research |
| 7 | Data/Stats | Key numbers, chart or callouts |
| 8 | Real-world examples | Use cases, case studies |
| 9 | Challenges/Limitations | Balanced perspective |
| 10 | Future Outlook | Trends, predictions |
| 11 | Key Takeaways | Summary, action items |
| 12 | Thank You / Q&A | Closing, contact info |

Adapt this structure to the specific topic and audience. Not every deck needs all 12 slides.

### 2b. Write Slide-by-Slide Content Plan

For each slide, specify:
- **Title**: Concise, engaging headline
- **Key points**: 3-5 bullets or content blocks
- **Visual idea**: Chart, icon, image, or layout suggestion
- **Data to highlight**: Any specific numbers or quotes

---

## Phase 3: Generate PPTX

### 3a. Choose Design Direction

Pick a color palette and visual motif from the pptx skill's design guidelines that fits the topic:

- **Tech/AI**: Ocean Gradient or Charcoal Minimal
- **Business/Finance**: Midnight Executive or Teal Trust
- **Health/Nature**: Forest & Moss or Sage Calm
- **Creative/Design**: Coral Energy or Berry & Cream
- **Social/Community**: Warm Terracotta or Cherry Bold

Apply the design principles from the pptx skill:
- One dominant color (60-70% visual weight)
- Dark/light "sandwich" (dark title + conclusion, light content)
- One consistent visual motif across all slides
- Varied layouts (never repeat the same layout twice in a row)

### 3b. Build with PptxGenJS

**Read [pptxgenjs.md](../pptx/pptxgenjs.md) for the full API reference.**

Create a single Node.js script that generates all slides. Key reminders:
- Use `LAYOUT_16x9` (10" × 5.625")
- Colors: NO `#` prefix — use `"FF6B35"` not `"#FF6B35"`
- Text arrays: use `breakLine: true` between lines
- Bullets: always use `bullet: true` in options, never unicode `•`
- Never reuse option objects — use factory functions
- Each presentation needs a fresh `pptxgen()` instance

### 3c. QA (Required)

Follow the pptx skill's QA workflow:

1. **Content QA**: Run `python -m markitdown output.pptx` and verify all content is present, no typos, no placeholder text
2. **Visual QA**: Convert to images and inspect with sub-agents (see pptx SKILL.md QA section)
3. **Fix-and-verify cycle**: Complete at least one round of fixes before declaring done

---

## Quick Reference

| Step | Action | Key Tool |
|------|--------|----------|
| Clarify | Ask about scope, audience, length | — |
| Research | 4-6 web searches, different angles | WebSearch |
| Synthesize | Compile findings into structured doc | — |
| Outline | Map to slide structure with visual ideas | — |
| Design | Pick palette, motif, fonts | — |
| Build | Write & run pptxgenjs script | pptxgenjs |
| QA | Content + visual inspection, fix cycle | markitdown + soffice + pdftoppm |

---

## Dependencies

- Same as the pptx skill (markitdown, pptxgenjs, LibreOffice, Poppler)
- WebSearch tool (built-in) for research phase
