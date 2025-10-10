# Lumora AI – WP Block Theme

Minimal, performance-first block theme following the Synima AI video agency page structure.

## Install
1. Copy `lumora-ai` to `wp-content/themes/`.
2. In WP Admin → Appearance → Themes, activate "Lumora AI".
3. Create a new Page (e.g. "AI videó ügynökség").
4. Insert patterns: Hero → Services Grid → Work Grid → CTA → FAQ.

## Patterns
- Hero: `Lumora / Hero - AI Video Agency`
- Services: `Lumora / Services Grid - AI Services`
- Work: `Lumora / Work Grid - Featured Projects`
- CTA: `Lumora / CTA - Free AI Consultation`
- FAQ: `Lumora / FAQ - AI Video`

## Performance checklist
- Images: upload WebP/AVIF, set `loading="lazy"` for below-the-fold.
- Fonts: use system stack (already) or preload WOFF2; `font-display: swap`.
- CSS: keep only used selectors; critical CSS in `assets/css/critical.css`.
- JS: keep modules small; load 3rd-party after consent.
- Cache/CDN: enable page cache + CDN (e.g., Cloudflare APO).

## SEO
- One H1 in Hero, H2 for sections.
- FAQ schema injected via `faq` pattern (JSON-LD).
- Set meta (OG/Twitter) via SEO plugin (Yoast/RankMath).

## A11y
- Sufficient color contrast (dark theme).
- Keyboard accessible details/summary for FAQ.


