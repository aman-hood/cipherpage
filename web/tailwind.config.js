/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0f172a',    // slate-900 background
          primary: '#3b82f6', // blue-500 (Used for Learn)
          accent: '#10b981',  // emerald-500 (Used for Grow)
          warning: '#f59e0b', // amber-500 (Used for Apply)
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
