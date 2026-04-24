const theme = (() => {
  const STORAGE_KEY = 'shoeshub-theme';
  const DEFAULT = 'minimal';

  function apply(name) {
    if (name === DEFAULT) {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', name);
    }
    localStorage.setItem(STORAGE_KEY, name);
    _updateToggleBtn(name);
  }

  function current() {
    return document.documentElement.getAttribute('data-theme') || DEFAULT;
  }

  function toggle() {
    apply(current() === DEFAULT ? 'original' : DEFAULT);
  }

  function _updateToggleBtn(name) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    const isOriginal = name === 'original';
    btn.textContent = isOriginal ? '🔵' : '🟡';
    btn.title = isOriginal ? 'Switch to Minimal' : 'Switch to Original';
  }

  // Apply saved theme immediately (before DOM renders) to prevent flash
  const saved = localStorage.getItem(STORAGE_KEY) || DEFAULT;
  if (saved !== DEFAULT) {
    document.documentElement.setAttribute('data-theme', saved);
  }

  return { apply, current, toggle };
})();
