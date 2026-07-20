// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
  site: 'https://notu.us',
  integrations: [
    starlight({
      title: 'notu.us — Mr. Nas\'s Briefcase',
      description: 'Educational materials, lesson plans, culture lab essays, music & dance — from Mr. Nas of Mohikontok Sound Lab',
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
              ],
            },
            {
              label: '📐 Math',
              collapsed: true,
              items: [
                { label: 'Overview', slug: 'lesson-plans/math' },
                { label: 'Ratios & Recipes', slug: 'lesson-plans/math/ratios-recipes' },
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
          items: [{ autogenerate: { directory: 'studio-skills' } }],
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
