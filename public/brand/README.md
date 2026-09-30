# Dot Panel brand kit

## Idea
One dot, one panel: a single red dot sits inside a rounded red panel beside two short content lines. It is an original geometric drawing, built from SVG primitives. The wordmark uses original outlined monoline capitals; no font file, stock artwork, external resource, or OpenAI logo is included.

Dot Panel is the product identity. The person's own dot name remains the main top-left app identity. Use a compact mark or small “Dot Panel” credit in the footer/about area rather than competing with that name. Do not suggest OpenAI sponsorship or affiliation.

## Assets
- `mark-dark.svg`: red/light mark for dark backgrounds, transparent canvas
- `mark-light.svg`: deep-red/black mark for light backgrounds, transparent canvas
- `mark-mono.svg`: single-color mark using `currentColor`; inline the SVG to inherit CSS color
- `wordmark-dark.svg`, `wordmark-light.svg`: fixed, font-independent outlined wordmarks; recommended
- `wordmark-editable-dark.svg`, `wordmark-editable-light.svg`: live-text title-case alternatives using system sans; appearance depends on the device font
- `favicon.svg`, `favicon.ico`: dark-backed app icon; ICO contains 16, 32, and 48px
- `favicon-16.png`, `favicon-32.png`, `favicon-180.png`, `favicon-512.png`: raster sizes
- `tokens.css`: copyable theme tokens
- `contrast.json`: calculated WCAG relative-luminance ratios
- `brand-preview.png`, `favicon-preview.png`: visual review sheets
- `generate.py`: editable source that regenerates SVG and tokens using Python's standard library
- `render.py`: optional PNG/ICO regeneration; requires CairoSVG and Pillow

## Palette
| Role | Hex |
|---|---|
| Canvas | `#0A0A0B` |
| Surface | `#161619` |
| Raised surface | `#222226` |
| Decorative border | `#35353C` |
| Primary text | `#F7F7F8` |
| Secondary text | `#A1A1AA` |
| Primary red | `#F04452` |
| Deep red | `#C62838` |

Use black for the majority of the interface; red is an action or emphasis color, with gray and white supporting hierarchy. Selected state must include a visible label/check or shape change, not color alone.

## Accessibility and application
- Near-black text on primary red: **5.33:1**. Use this pairing for vivid-red filled actions
- Off-white text on deep red: **5.21:1**. Use this pairing if light button labels are preferred
- Primary text on canvas: **18.48:1**; secondary text on canvas: **7.72:1**
- Primary red on raised surface: **4.27:1**; use for icons/focus indicators, not small normal text
- Decorative border is subtle and must not be the only means of identifying a control
- Minimum touch target: 48px. Control radius 14px, panel radius 22px; retain a clear visible keyboard focus indicator
- Use system sans for UI. Keep supporting labels readable and avoid turning the outlined logo alphabet into a UI font
- SVG mark native size is 32px; use at least 16px. Wordmark recommended width at least 156px (24px height)
- Leave at least 8px clear space around a 32px mark; scale clear space proportionally
- SVGs contain accessible titles. For `<img>`, give the logo an `alt="Dot Panel"`; if adjacent visible text already supplies the name, use `alt=""`

## Header example
```html
<link rel="icon" type="image/svg+xml" href="/brand/favicon.svg">
<link rel="icon" href="/brand/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/brand/favicon-180.png">
```

The kit makes no trademark clearance or affiliation claim. The repository's maintainer should determine the applicable licensing for the published project; this kit does not add a conflicting license.
