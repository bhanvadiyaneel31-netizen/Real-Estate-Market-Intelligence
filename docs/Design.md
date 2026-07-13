# Design.md — Visual System for the Dashboard

## 1. Theme
- Light mode as default; dark mode optional stretch goal.
- Clean, data-dense but not cluttered — this is an analytics tool, not a marketing site.

## 2. Color Palette
| Role | Color | Use |
|---|---|---|
| Primary | Deep blue (`#1E3A8A`) | Primary buttons, active nav, key chart lines |
| Secondary | Teal (`#0D9488`) | Secondary chart series, accents |
| Success | Green (`#16A34A`) | "Good deal" / under-market indicators |
| Warning | Amber (`#D97706`) | "Above market" / risk indicators |
| Danger | Red (`#DC2626`) | Errors, high-risk flags |
| Neutral background | Off-white (`#F8FAFC`) | Page background |
| Neutral surface | White (`#FFFFFF`) | Cards, panels |
| Text primary | Slate 900 (`#0F172A`) | Headings, key text |
| Text secondary | Slate 500 (`#64748B`) | Labels, captions |
| Border | Slate 200 (`#E2E8F0`) | Card borders, dividers |

## 3. Typography
- Font: Inter (or system-ui fallback) for UI text.
- Headings: semi-bold, tight tracking.
- Body: regular weight, 14–16px base size.
- Numbers/metrics (prices, percentages): tabular-nums so figures align in tables.

## 4. Layout
- Sidebar navigation (Overview / Predictor / Similar Properties / Model Comparison / Explorer) on desktop; collapsible on mobile.
- Cards with consistent padding (16–24px), subtle border, minimal shadow.
- Charts get generous whitespace — avoid cramming multiple chart types into one card.

## 5. Component Conventions
- Buttons: primary (filled, deep blue), secondary (outline), destructive (red outline) — no more than one filled primary button per view.
- Forms: label above input, inline validation errors in red, helper text in slate-500.
- Tables: sticky header, zebra striping optional, sortable columns for the Listing Explorer.
- Loading states: skeleton placeholders matching the shape of the real content — no generic spinners for data-heavy views.
- Empty states: short message + icon, never a blank card.

## 6. Charts (Recharts)
- Consistent color mapping per model across all charts (e.g. XGBoost always teal, Random Forest always blue) so the Model Comparison view stays legible over time.
- Tooltips show exact values on hover; axis labels always visible, no reliance on tooltip-only data.
