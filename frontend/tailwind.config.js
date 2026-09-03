/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand palette — deep space / cloud theme
        primary: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        // Accent — electric teal for highlights and actions
        accent: {
          50:  "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
          700: "#0e7490",
          800: "#155e75",
          900: "#164e63",
        },
        // Semantic success / warning / danger
        success: "#10b981",
        warning: "#f59e0b",
        danger:  "#ef4444",
        // Dark background shades
        dark: {
          900: "#0a0e1a",
          800: "#0f1629",
          700: "#151d35",
          600: "#1c2645",
          500: "#243058",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        glow:      "0 0 20px rgba(99,102,241,0.35)",
        "glow-sm": "0 0 10px rgba(99,102,241,0.25)",
        card:      "0 4px 24px rgba(0,0,0,0.4)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "mesh-dark":
          "radial-gradient(at 40% 20%, hsla(228,100%,15%,1) 0px, transparent 50%), " +
          "radial-gradient(at 80% 0%,  hsla(249,100%,15%,1) 0px, transparent 50%), " +
          "radial-gradient(at 0%  50%, hsla(220,100%,10%,1) 0px, transparent 50%)",
      },
      animation: {
        "fade-in":    "fadeIn 0.4s ease-out",
        "slide-in":   "slideIn 0.35s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 },                    to: { opacity: 1 } },
        slideIn: { from: { opacity: 0, transform: "translateY(8px)" }, to: { opacity: 1, transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
}
