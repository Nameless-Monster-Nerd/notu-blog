// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
  site: 'https://notu.us',
  integrations: [
    starlight({
      title: 'notu.us — Mr. Nas\'s Briefcase',
      description: 'Free STEAM worksheets, lesson plans, Bengali culture essays, Bronx music studio, and BaFA dance classes — from Mr. Nas of Mohikontok Sound Lab in the Bronx, NY.',
      head: [
        // Open Graph / Social meta tags
        { tag: 'meta', attrs: { property: 'og:type', content: 'website' } },
        { tag: 'meta', attrs: { property: 'og:site_name', content: 'notu.us — Mr. Nas\'s Briefcase' } },
        { tag: 'meta', attrs: { property: 'og:locale', content: 'en_US' } },
        { tag: 'meta', attrs: { name: 'twitter:card', content: 'summary_large_image' } },
        { tag: 'meta', attrs: { name: 'twitter:site', content: '@mohikontok' } },
        // SEO
        { tag: 'meta', attrs: { name: 'robots', content: 'index, follow' } },
        { tag: 'meta', attrs: { name: 'keywords', content: 'STEAM worksheets, Bronx music studio, Bengali culture, lesson plans, Mohikontok Sound Lab, Mr. Nas, free educational resources, Bronx arts, soundproofing guide, dance classes Bronx' } },
      ],
      logo: {
        src: '/src/assets/notu-logo.svg',
        replacesTitle: true,
      },
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/Nameless-Monster-Nerd/notu-blog' },
      ],
      customCss: [
        './src/styles/custom.css',
      ],
      sidebar: [
        {
          label: '📖 Culture Lab',
          items: [
            { label: 'Bengali Heritage', slug: 'culture-lab/bengali-heritage' },
            { label: 'Bronx Arts & Community', slug: 'culture-lab/bronx-arts' },
            { label: 'Dance as Healing', slug: 'culture-lab/dance-as-healing' },
            { label: '🎭 Kathak Series', slug: 'culture-lab/kathak-history-part-1' },
                      { label: '🎭 Part 2', slug: 'culture-lab/kathak-history-part-2' },
          ],
        },
        {
          label: '🎵 Music & Sound',
          items: [{ autogenerate: { directory: 'music-sound' } }],
        },
        {
          label: '💃 Dance & Movement',
          items: [{ autogenerate: { directory: 'dance-movement' } }],
        },
        {
          label: '📚 Lesson Plans',
          items: [
            { label: 'Overview', slug: 'lesson-plans' },
            {
              label: '🔬 Science',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/science' },
                { label: 'Matter & Particles', slug: 'lesson-plans/science/matter-particles' },
                { label: 'Energy in Motion', slug: 'lesson-plans/science/energy-in-motion' },
                { label: 'Waves, Sound & Light', slug: 'lesson-plans/science/waves-sound-light' },
                { label: 'Earth Systems', slug: 'lesson-plans/science/earth-systems' },
              ],
            },
            {
              label: '📐 Math',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/math' },
                { label: 'Ratios & Recipes', slug: 'lesson-plans/math/ratios-recipes' },
                { label: 'Number System', slug: 'lesson-plans/math/number-system' },
              ],
            },
            {
              label: '⚙️ Engineering',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/engineering' },
                { label: 'Simple Machines', slug: 'lesson-plans/engineering/simple-machines' },
              ],
            },
            {
              label: '🎨 Arts',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/arts' },
                { label: 'Colors & Emotions', slug: 'lesson-plans/arts/colors-emotions' },
              ],
            },
            {
              label: '💻 Technology',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/technology' },
                { label: 'Algorithms', slug: 'lesson-plans/technology/algorithms-everyday' },
              ],
            },
          ],
        },
        {
          label: '🛠️ Studio Skills',
          items: [
            { label: 'Overview', slug: 'studio-skills' },
            {
              label: '🔇 Soundproofing',
              collapsed: true,
              items: [
                { label: 'Under $200', slug: 'studio-skills/soundproof-under-200' },
                { label: 'DIY Acoustic Panels', slug: 'studio-skills/diy-acoustic-panels' },
                { label: 'The $65/hr Model', slug: 'studio-skills/soundproof-space-model' },
              ],
            },
            {
              label: '🎙️ Recording',
              collapsed: true,
              items: [
                { label: 'Mic Placement', slug: 'studio-skills/mic-placement' },
                { label: 'Home Studio Setup', slug: 'studio-skills/home-studio-setup' },
              ],
            },
            {
              label: '🎛️ Production',
              collapsed: true,
              items: [
                { label: 'Mixing for Beginners', slug: 'studio-skills/mixing-basics' },
              ],
            },
          ],
        },
        {
          label: '📰 Blog',
          items: [{ autogenerate: { directory: 'blog' } }],
        },
        {
          label: '📋 About Mr. Nas',
          slug: 'about/mr-nas',
        },
      ],
    }),
  ],
});
