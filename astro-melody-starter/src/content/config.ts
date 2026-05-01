import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const posts = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "src/content/posts" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.date(),
    description: z.string(),
    lastModified: z.string().optional(),
    cover: z.string(),
    coverAlt: z.string(),
    category: z.array(z.string()),
    tags: z.array(z.string()),
    author: z.string().optional(),
    pinOrder: z.number().optional(),
  }),
});

const videos = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "src/content/videos" }),
  schema: z.object({
    title: z.string(),
    series: z.string(),
    description: z.string(),
    pubDate: z.string(),
    cover: z.string().optional(),
    category: z.array(z.string()),
    tags: z.array(z.string()),
    videoCount: z.number(),
    videos: z.array(
      z.object({
        name: z.string(),
        hlsUrl: z.string(),
      })
    ),
  }),
});

export const collections = { posts, videos };
