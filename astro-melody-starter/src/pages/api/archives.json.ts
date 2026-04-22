import { getCollection } from "astro:content";

export async function GET() {
  const allPosts = await getCollection("posts");

  allPosts.sort(
    (a, b) =>
      new Date(b.data.pubDate).valueOf() - new Date(a.data.pubDate).valueOf(),
  );

  const postsData = allPosts.map((post) => ({
    id: post.id,
    title: post.data.title,
    pubDate: post.data.pubDate,
    url: `/posts/${post.id}/`,
  }));

  return new Response(JSON.stringify(postsData), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
  });
}
