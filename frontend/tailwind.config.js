/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          900: '#0B0F19',
          950: '#070A12',
        },
        surface: {
          DEFAULT: '#151C2C',
          light: '#1E293B',
          border: '#334155',
        },
        warranty: {
          teal: '#10B981',
          emerald: '#059669',
        },
        recall: {
          crimson: '#EF4444',
          rose: '#DC2626',
        },
        diagnostic: {
          amber: '#F59E0B',
          orange: '#F97316',
        }
      },
      fontFamily: {
        space: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
