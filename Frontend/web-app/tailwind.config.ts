import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        clearly: {
          obsidian: "#1B1B1B",
          baltic: "#394E96",
          royal: "#4277FF",
          "royal-hover": "#2B5FE8",
          birch: "#C5C1B9",
          "birch-light": "#F2F0EB",
          paper: "#FAFAFA",
          cream: "#F7F5F0",
          success: "#0D7A3E",
          "success-bg": "#E8F5E9",
          warning: "#A85300",
          "warning-bg": "#FFF3E0",
          danger: "#C5192D",
          "danger-bg": "#FFEBEE",
        },
        contrast: {
          bg: "#000000",
          text: "#FFFF00",
          border: "#FFFF00",
          cyan: "#00FFFF",
          white: "#FFFFFF",
        },
      },
      fontFamily: {
        atkinson: ["var(--font-atkinson)", "Atkinson Hyperlegible", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

