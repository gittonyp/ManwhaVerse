import './styles/global.css'
import { mount } from 'svelte'
import App from './App.svelte'

console.log('[Main] Starting app mount...');

try {
  const app = mount(App, {
    target: document.getElementById('app'),
  });
  console.log('[Main] App mounted successfully');
} catch (err) {
  console.error('[Main] CRITICAL ERROR during mount:', err);
}
