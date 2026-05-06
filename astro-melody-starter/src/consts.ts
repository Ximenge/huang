// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

// Base Page Metadata, src/layouts/BaseLayout.astro
export const BRAND_NAME = "91图图";
export const SITE_TITLE = "91图图";
export const META_TITLE = "91图图网-分享精选优质写真福利套图，视频全收集 |Cosplay|二次元|写真|福利|图包|美图";
export const SITE_DESCRIPTION = "91图图网-分享精选优质写真福利套图，视频全收集 |Cosplay|二次元|写真|福利|图包|美图";
export const LIGHT_THEME = 'corporate';
export const DARK_THEME = 'halloween';

// Tags Page Metadata, src/pages/tags/index.astro
export const Tags_TITLE = "91图图 - 所有标签";
export const Tags_DESCRIPTION =
  "91图图 - 所有标签和相关文章数量";

// Tags Page Metadata, src/pages/tags/[tag]/[page].astro
export function getTagMetadata(tag: string) {
  return {
    title: `91图图 - '${tag}' 标签下的所有文章`,
    description: `探索91图图中关于 ${tag} 的文章，从不同角度进行深入分析。`,
  };
}

// Category Page Metadata, src/pages/category/[category]/[page].astro
export function getCategoryMetadata(category: string) {
  return {
    title: `91图图 - '${category}' 分类下的所有文章`,
    description: `浏览91图图中 ${category} 分类下的所有文章`,
  };
}

// Header Links, src/components/Header.astro
export const HeaderLinks = [
  { href: "/category/R18/1/", title: "R18" },
  { href: "/category/R17/1/", title: "R17" },
  { href: "/category/R16/1/", title: "R16" },
];

// Footer Links, src/components/Footer.astro
export const FooterLinks: Array<{ href: string; title: string }> = [];

// Social Links, src/components/Footer.astro
export const SocialLinks = [
  { href: "/rss.xml", icon: "icon-[tabler--rss]", label: "RSS" },
];

export const POPUNDER_ENABLED = false;
export const POPUNDER_IDZONE = "5866630";
export const POPUNDER_FREQUENCY_PERIOD = 60;
export const POPUNDER_FREQUENCY_COUNT = 1;
export const POPUNDER_TRIGGER_METHOD = 1;

export const DOWNLOAD_POPUNDER_ENABLED = true;
export const DOWNLOAD_POPUNDER_IDZONE = "5914280";

export const VIDEO_VAST_AD_ENABLED = true;
export const VIDEO_VAST_AD_TAG = `https://s.magsrv.com/v1/vast.php?idzone=5865438`;

export const AGE_VERIFICATION_ENABLED = false;

export const PIN_ORDER_ENABLED = true;

// Search Page Metadata, src/pages/search.astro
export const SEARCH_PAGE_TITLE = `${SITE_TITLE} - 站点搜索`;
export const SEARCH_PAGE_DESCRIPTION = `搜索 ${SITE_TITLE} 上的所有内容`;
