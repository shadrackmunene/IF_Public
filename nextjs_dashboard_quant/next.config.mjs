/** Static export: `npm run build` writes plain HTML/JS/CSS to ./out, which any static host can serve
 *  (Vercel, Netlify, GitHub Pages, Azure Static Web Apps). No server runs at view time.
 *  Set NEXT_PUBLIC_BASE_PATH (e.g. "/IF_Public") when hosting under a sub-path such as GitHub Pages. */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  basePath,
};

export default nextConfig;
