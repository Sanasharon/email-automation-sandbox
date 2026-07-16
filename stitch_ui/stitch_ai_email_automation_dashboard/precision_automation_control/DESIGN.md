---
name: Precision Automation Control
colors:
  surface: '#f8f9ff'
  surface-dim: '#d4dae5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eef4ff'
  surface-container: '#e8eef9'
  surface-container-high: '#e2e9f4'
  surface-container-highest: '#dce3ee'
  on-surface: '#151c24'
  on-surface-variant: '#424753'
  inverse-surface: '#2a3139'
  inverse-on-surface: '#ebf1fc'
  outline: '#727785'
  outline-variant: '#c2c6d6'
  surface-tint: '#005bc0'
  primary: '#0051ae'
  on-primary: '#ffffff'
  primary-container: '#0969da'
  on-primary-container: '#ecefff'
  inverse-primary: '#adc6ff'
  secondary: '#5b5e66'
  on-secondary: '#ffffff'
  secondary-container: '#dfe2eb'
  on-secondary-container: '#61646c'
  tertiary: '#913900'
  on-tertiary: '#ffffff'
  tertiary-container: '#b84b00'
  on-tertiary-container: '#ffece5'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#dfe2eb'
  secondary-fixed-dim: '#c3c6cf'
  on-secondary-fixed: '#181c22'
  on-secondary-fixed-variant: '#43474e'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb693'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7a2f00'
  background: '#f8f9ff'
  on-background: '#151c24'
  surface-variant: '#dce3ee'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  headline-md-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  sidebar-width: 260px
  header-height: 64px
  container-max: 1280px
  gutter: 1rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style
The design system is engineered for high-stakes enterprise AI automation, where clarity, speed of cognition, and reliability are paramount. The brand personality is clinical, efficient, and authoritative, evoking the feel of a sophisticated terminal translated into a modern web interface.

The visual style is **High-Contrast Minimalism**. It eschews decorative trends like gradients and glassmorphism in favor of a rigid, grid-based layout that prioritizes information density and legibility. By utilizing a "Flat 2.0" approach, depth is communicated through subtle 1px borders and purposeful shifts in background tokens rather than shadows or depth effects.

## Colors
The palette is rooted in a functional "Status-First" logic. 
- **Primary & Secondary:** A deep Navy (#0D1117) provides a grounding force for the navigation, while System Blue (#0969DA) acts as the high-visibility driver for actions.
- **Surface & Borders:** The interface uses #F9FAFB as the canvas. Separation between elements is achieved exclusively via 1px solid borders (#D0D7DE), creating a "blueprint" aesthetic.
- **Semantic Feedback:** Success, Error, and Warning states utilize high-contrast pairings (light background/dark text) to ensure accessibility and rapid status scanning within dense email lists.

## Typography
The design system utilizes **Inter** exclusively to leverage its exceptional legibility at small sizes and high-density environments. 

Headings are rendered with heavier weights (600 or 700) and tighter letter spacing to create a strong visual anchor. Body copy is kept at a comfortable 14px or 16px for sustained reading of automated email drafts. Labels and metadata use a slightly tracked-out 12px font to differentiate technical data from human-readable content.

## Layout & Spacing
The layout follows a **Fixed Sidebar + Fluid Content** model.
- **Desktop:** A permanent 260px sidebar is anchored to the left, utilizing the #0D1117 background. The main content area lives within a 1280px maximum container, centered on the screen to prevent line lengths from becoming unreadable on ultra-wide monitors.
- **Mobile:** The sidebar collapses into a hidden drawer, triggered by a persistent top header.
- **Grid:** A rigid 8px spacing system governs all margins and padding. White space is generous around major modules to prevent the AI data from feeling overwhelming.

## Elevation & Depth
Depth is strictly flat. This design system communicates hierarchy through **Tonal Layering** and **Outline Reinforcement** rather than shadows.

- **Level 0 (Background):** #F9FAFB.
- **Level 1 (Cards/Modules):** White (#FFFFFF) surfaces with a 1px #D0D7DE border.
- **Level 2 (Modals/Popovers):** White surfaces with a slightly darker 1px border (#8C959F).

No shadows are permitted. Interaction states (hover/active) are indicated by subtle background color shifts (e.g., #F3F4F6) or border color changes, never by "lifting" the element.

## Shapes
The shape language is disciplined and geometric. 
- **Modules & Inputs:** A consistent 6px corner radius is applied to cards, buttons, and input fields. This provides just enough softness to feel modern without sacrificing the "industrial" enterprise aesthetic.
- **Badges:** Status indicators utilize a "pill" shape (full rounding) to visually distinguish them from interactive buttons or data fields.

## Components
- **Cards:** White background, 1px #D0D7DE border, 6px border-radius. No padding should be less than 24px (1.5rem) to maintain the "generous white space" mandate.
- **Buttons:** Primary buttons are solid Blue (#0969DA) with white text. Secondary buttons are white with a 1px border. All buttons use 6px rounding.
- **Status Badges:** Pill-shaped. Use semantic color pairs (e.g., Success: #DAFBE1 bg / #1A7F37 text). Text should be uppercase and bold for quick identification.
- **Data Tables:** No vertical borders. Rows have a 1px #D0D7DE bottom border. Header row uses a light gray background (#F6F8FA) and bold labels.
- **Input Fields:** 1px border with a 6px radius. Focus state is a 1px Blue (#0969DA) border with a soft 2px blue "glow" (not a shadow, but a CSS outline).
- **Sidebar Nav:** High-contrast Navy background with light gray text (#8B949E). Active state uses white text and a 2px blue vertical "indicator" on the far left of the item.