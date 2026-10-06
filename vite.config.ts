import adapterCloudflare from '@sveltejs/adapter-cloudflare';
import adapterNetlify from '@sveltejs/adapter-netlify';
import adapterNode from '@sveltejs/adapter-node';
import adapterVercel from '@sveltejs/adapter-vercel';
import { env } from 'node:process';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

function getAdapter(target: string) {
  switch (target) {
    case 'cloudflare':
      return adapterCloudflare();
    case 'netlify':
      return adapterNetlify();
    case 'render':
      return adapterNode();
    case 'vercel':
      return adapterVercel();
    default:
      throw new Error(`Unsupported DEPLOY_TARGET "${target}".`);
  }
}

export default defineConfig({
  plugins: [
    sveltekit({
      adapter: getAdapter(env.DEPLOY_TARGET ?? 'render'),
      preprocess: vitePreprocess()
    })
  ]
});
