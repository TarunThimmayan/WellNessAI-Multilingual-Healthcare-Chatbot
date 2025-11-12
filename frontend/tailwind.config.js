/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        ocean: {
          50: '#f2fbfb',
          100: '#d4f6f3',
          200: '#a9ebe5',
          300: '#77d7d3',
          400: '#46bebd',
          500: '#2ea5a7',
          600: '#22908f',
          700: '#1d7272',
          800: '#1b595a',
          900: '#1a4a4b',
        },
        mint: {
          50: '#f4fdf7',
          100: '#e6fbe9',
          200: '#c6f6d1',
          300: '#95edaf',
          400: '#5fd186',
          500: '#36b060',
          600: '#29934d',
          700: '#237540',
          800: '#1f5d34',
          900: '#1b4d2d',
        },
      },
      boxShadow: {
        glass: '0 20px 45px -20px rgba(13, 148, 136, 0.35)',
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: 0.45 },
          '50%': { opacity: 1 },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.4s ease-out forwards',
        pulseGlow: 'pulseGlow 2.4s ease-in-out infinite',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

