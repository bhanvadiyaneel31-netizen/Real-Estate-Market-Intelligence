---
name: Professional Analytics
colors:
  surface: '#FFFFFF'
  surface-dim: '#dad9e1'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3fa'
  surface-container: '#eeedf4'
  surface-container-high: '#e9e7ef'
  surface-container-highest: '#e3e1e9'
  on-surface: '#1a1b21'
  on-surface-variant: '#444651'
  inverse-surface: '#2f3036'
  inverse-on-surface: '#f1f0f7'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#4b1c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#6e2c00'
  on-tertiary-container: '#f39461'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb691'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#773205'
  background: '#faf8ff'
  on-background: '#1a1b21'
  surface-variant: '#e3e1e9'
  success: '#16A34A'
  warning: '#D97706'
  danger: '#DC2626'
  bg-base: '#F8FAFC'
  text-primary: '#0F172A'
  text-secondary: '#64748B'
  border: '#E2E8F0'
typography:
  display:
    fontFamily: inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  metric-lg:
    fontFamily: inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  metric-sm:
    fontFamily: inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  margin-mobile: 1rem
  margin-desktop: 1.5rem
  gutter: 1rem
  card-padding-sm: 1rem
  card-padding-lg: 1.5rem
---

# Visual System: Analytics Dashboard

## 1. Theme
- **Default**: Light mode.
- **Style**: Clean, data-dense, professional analytics aesthetic. No clutter.

## 2. Color Palette
- **Primary**: Deep Blue (#1E3A8A) - Primary buttons, active nav, key chart lines.
- **Secondary**: Teal (#0D9488) - Secondary chart series, accents.
- **Success**: Green (#16A34A) - "Good deal" / under-market indicators.
- **Warning**: Amber (#D97706) - "Above market" / risk indicators.
- **Danger**: Red (#DC2626) - Errors, high-risk flags.
- **Background**: Off-white (#F8FAFC).
- **Surface**: White (#FFFFFF) - Cards, panels.
- **Text Primary**: Slate 900 (#0F172A).
- **Text Secondary**: Slate 500 (#64748B).
- **Border**: Slate 200 (#E2E8F0).

## 3. Typography
- **Font**: Inter (system-ui fallback).
- **Headings**: Semi-bold, tight tracking.
- **Body**: Regular weight, 14–16px base size.
- **Metrics**: Tabular-nums for aligned figures in tables/prices.

## 4. Layout (Mobile Focus)
- **Navigation**: Collapsible sidebar / Bottom navigation for mobile.
- **Cards**: 16–24px padding, subtle border (Slate 200), minimal shadow.
- **Charts**: Generous whitespace, focused one-chart-per-card approach.

## 5. Components
- **Buttons**:
  - Primary: Filled, Deep Blue.
  - Secondary: Outline.
  - Destructive: Red Outline.
- **Forms**: Labels above inputs, inline red validation, slate-500 helper text.
- **Tables**: Sticky headers, sortable columns.
- **States**: Skeleton placeholders for loading; short message + icon for empty states.

## 6. Data Visualization
- **Recharts**: Consistent color mapping (XGBoost: Teal, Random Forest: Blue).
- **Tooltips**: Exact values on hover, persistent axis labels.