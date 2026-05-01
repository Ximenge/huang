import type { CollectionEntry } from "astro:content";
import { PIN_ORDER_ENABLED } from "@consts";

export function sortPosts(posts: CollectionEntry<"posts">[]): CollectionEntry<"posts">[] {
  const sorted = [...posts];
  sorted.sort(
    (a, b) =>
      new Date(b.data.pubDate).valueOf() - new Date(a.data.pubDate).valueOf(),
  );

  if (!PIN_ORDER_ENABLED) {
    return sorted;
  }

  const pinned = sorted.filter((p) => p.data.pinOrder != null);
  const unpinned = sorted.filter((p) => p.data.pinOrder == null);

  pinned.sort((a, b) => (a.data.pinOrder ?? 0) - (b.data.pinOrder ?? 0));

  return [...pinned, ...unpinned];
}
