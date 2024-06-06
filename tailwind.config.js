/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {
      backgroundImage:{
        'app-background' : "url(/static/assets/background5.jpg)",
      }
    },
  },
  plugins: [],
}

