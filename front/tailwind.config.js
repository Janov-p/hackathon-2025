/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cm-red': 'rgb(226, 0, 26)',
        'cm-dark': 'rgb(62, 62, 64)',
        'cm-gray': 'rgb(229, 231, 235)',
      },
    },
  },
  plugins: [],
}
