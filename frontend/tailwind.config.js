/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg:      "#0d0f14",
        surface: "#151820",
        panel:   "#1a1d26",
        border:  "#252836",
        accent:  "#7c6ff7",
      }
    }
  },
  plugins: []
}
