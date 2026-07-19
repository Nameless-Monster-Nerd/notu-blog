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
          items: [{ autogenerate: { directory: 'lesson-plans' } }],
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
