/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",       // Deep blue
        secondary: "#0D9488",     // Teal
        success: "#16A34A",       // Green
        warning: "#D97706",       // Amber
        danger: "#DC2626",        // Red
        neutral: {
          background: "#F8FAFC",  // Off-white
          surface: "#FFFFFF",     // White
        },
        text: {
          primary: "#0F172A",     // Slate 900
          secondary: "#64748B",   // Slate 500
        },
        border: "#E2E8F0",        // Slate 200
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
