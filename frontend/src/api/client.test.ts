import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

describe('api client base URL resolution', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it('uses the API URL provided via environment variables', async () => {
    vi.stubEnv('VITE_API_URL', 'https://api.example.com')

    const { default: api } = await import('./client')

    expect(api.defaults.baseURL).toBe('https://api.example.com')
  })

  it('falls back to the current origin when no environment URL is provided', async () => {
    const { default: api } = await import('./client')

    expect(api.defaults.baseURL).toBe(`${window.location.origin}/api`)
  })

  it('falls back to a relative /api path when the window object is unavailable', async () => {
    const originalWindow = globalThis.window
    vi.stubGlobal('window', undefined as unknown as Window & typeof globalThis)

    const { default: api } = await import('./client')

    expect(api.defaults.baseURL).toBe('/api')

    if (originalWindow) {
      vi.stubGlobal('window', originalWindow)
    }
  })
})
