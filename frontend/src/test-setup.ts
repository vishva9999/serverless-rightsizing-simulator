import '@testing-library/jest-dom';

// Polyfill ResizeObserver for Recharts in JSDOM
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = ResizeObserverMock as any;
window.ResizeObserver = ResizeObserverMock as any;

// Mock Leaflet in JSDOM environment if needed
if (typeof window !== 'undefined') {
  // Polyfill URL.createObjectURL
  if (!window.URL.createObjectURL) {
    window.URL.createObjectURL = () => '';
  }
}
