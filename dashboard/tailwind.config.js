/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12222E",
        "ink-2": "#1B3446",
        "ink-3": "#294A61",
        paper: "#F3F0E7",
        "paper-dim": "#E7E2D2",
        signal: {
          red: "#C6432B",
          "red-dim": "#F4E1DC",
          amber: "#C68A2B",
          "amber-dim": "#F5E9D6",
          green: "#3E7A55",
          "green-dim": "#DEEAE2",
        },
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
