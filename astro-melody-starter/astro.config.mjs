// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

import sitemap from "@astrojs/sitemap";
import { remarkModifiedTime } from "./src/utils/remark-modified-time.mjs";
import partytown from "@astrojs/partytown";
import pagefind from "astro-pagefind";
import tailwindcss from "@tailwindcss/vite";

import cloudflare from "@astrojs/cloudflare";

// https://astro.build/config
export default defineConfig({
  vite: {
    // @ts-ignore - Tailwind CSS plugin type compatibility issue with Vite
    plugins: [tailwindcss()],
  },

  site: "https://91tutu.cc",
  trailingSlash: "always",
  output: "static",

  prefetch: {
    prefetchAll: true,
    defaultStrategy: "viewport",
  },

  experimental: {},

  image: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
    ],
  },

  markdown: {
    remarkPlugins: [remarkModifiedTime],
  },

  integrations: [
    mdx(),
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      filter: (page) => !page.includes('/404'),
    }),
    pagefind(),

    partytown({
      config: {
        forward: ["dataLayer.push"],
        debug: false,
      },
    }),
  ],

  adapter: cloudflare(),
});