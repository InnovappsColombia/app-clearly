import type { Metadata, Viewport } from "next";
import "./globals.css";
import { A11yProvider } from "../context/A11yContext";
import { A11yToolbar } from "../components/a11y/A11yToolbar";
import { AccessibleTTSPlayer } from "../components/tts/AccessibleTTSPlayer";

export const metadata: Metadata = {
  title: "CLEARLY — Tu comunidad. Más clara. (WCAG 2.1 AAA)",
  description:
    "Ecosistema omnicanal de inclusión ciudadana, accesibilidad digital gerontológica y traducción de documentos gubernamentales a lenguaje claro.",
  authors: [{ name: "CLEARLY Initiative - Navreet Pabla" }],
  keywords: [
    "Accesibilidad",
    "WCAG AAA",
    "Adultos Mayores",
    "Plain Language",
    "Atkinson Hyperlegible",
    "Brampton",
    "Inmigración",
    "Traducción Documental",
  ],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1.0,
  maximumScale: 5.0,
  userScalable: true,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="theme-light">
      <body className="min-h-screen antialiased bg-[#F7F5F0] dark:bg-[#121212] text-[#1B1B1B] dark:text-[#F3F4F6] transition-colors duration-200">
        <A11yProvider>
          {/* Accessible Top Toolbar */}
          <A11yToolbar />

          {/* Main Application Content */}
          <main id="main-content" tabIndex={-1} className="outline-none">
            {children}
          </main>

          {/* In-Browser Accessible TTS Floating Audio Player */}
          <AccessibleTTSPlayer />
        </A11yProvider>
      </body>
    </html>
  );
}
