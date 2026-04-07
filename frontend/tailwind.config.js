/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#05070F',
        abyss: '#091226',
        cyanGlow: '#06F7FF',
        violetGlow: '#7E5BFF',
        blueGlow: '#1F8BFF',
      },
      fontFamily: {
        display: ['Sora', 'sans-serif'],
        body: ['Space Grotesk', 'sans-serif'],
      },
      boxShadow: {
        neon: '0 0 0 1px rgba(6,247,255,0.35), 0 0 30px rgba(6,247,255,0.18)',
        violet: '0 0 0 1px rgba(126,91,255,0.35), 0 0 26px rgba(126,91,255,0.2)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
