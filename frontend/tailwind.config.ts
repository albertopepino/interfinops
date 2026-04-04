import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#e8f4fd', 100: '#c5e3f9', 200: '#8ec8f3', 300: '#57adec',
          400: '#2d92d9', 500: '#1a6fb5', 600: '#155d98', 700: '#104b7b',
          800: '#0c3a5f', 900: '#082a45', 950: '#051a2d',
        },
        accent: {
          50: '#f0faf0', 100: '#d4f0d4', 200: '#a8e0a8', 300: '#7ccf7c',
          400: '#5cb85c', 500: '#4caa4c', 600: '#3d8b3d', 700: '#2e6c2e',
        },
      },
      fontFamily: {
        sans: ['DM Sans', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        mono: ['Space Mono', 'SF Mono', 'monospace'],
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
