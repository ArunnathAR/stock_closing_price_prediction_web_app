/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#2962FF',
        'primary-dark': '#0039CB',
        'primary-light': '#768FFF',
        'secondary': '#00C853',
        'secondary-dark': '#009624',
        'secondary-light': '#5EFF82',
        'warning': '#FF6B6B',
        'warning-dark': '#C73E3E',
        'warning-light': '#FF9E9E',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'heading': ['Poppins', 'sans-serif'],
        'mono': ['Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}