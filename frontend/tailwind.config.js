/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#080c14',
          surface: '#0d131f',
          card: '#131b2e',
          cardHover: '#18223a',
          border: '#1e293b',
          borderBright: '#334155',
          cyan: '#06b6d4',
          cyanGlow: 'rgba(6, 182, 212, 0.15)',
          amber: '#f59e0b',
          amberGlow: 'rgba(245, 158, 11, 0.15)',
          red: '#ef4444',
          redGlow: 'rgba(239, 68, 68, 0.15)',
          emerald: '#10b981',
          emeraldGlow: 'rgba(16, 185, 129, 0.15)',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 15px -3px rgba(6, 182, 212, 0.3)',
        'glow-red': '0 0 15px -3px rgba(239, 68, 68, 0.3)',
        'glow-amber': '0 0 15px -3px rgba(245, 158, 11, 0.3)',
      },
    },
  },
  plugins: [],
}
