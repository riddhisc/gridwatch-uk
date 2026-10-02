/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        grid: {
          ink: "#f8fafc",
          panel: "#ffffff",
          line: "#cbd5e1",
          accent: "#1d4ed8",
          success: "#15803d",
          warn: "#b45309",
          danger: "#b91c1c",
        },
      },
    },
  },
  plugins: [],
};
