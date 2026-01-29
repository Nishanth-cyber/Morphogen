/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        chat: {
          user: '#0ea5e9',
          assistant: '#f3f4f6',
          system: '#fef3c7',
        }
      }
    },
  },
  plugins: [],
}
