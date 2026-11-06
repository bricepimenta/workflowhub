import { defineConfig } from 'vite';

// `test` is read by Vitest (npm test); Vite itself ignores it during dev/build.
export default defineConfig({
  test: {
    environment: 'jsdom',
  },
});
