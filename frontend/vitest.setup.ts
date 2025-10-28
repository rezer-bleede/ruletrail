import '@testing-library/jest-dom/vitest'

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (!globalThis.ResizeObserver) {
  // Headless UI relies on ResizeObserver for transitions; jsdom does not ship it by default.
  // Providing a minimal mock keeps dialog components functional in tests.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ;(globalThis as any).ResizeObserver = ResizeObserverMock
}
