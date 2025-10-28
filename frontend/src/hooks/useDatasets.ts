import { useEffect, useState } from 'react'
import api from '../api/client'
import { Dataset } from '../types'

export function useDatasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = () => {
    setLoading(true)
    api
      .get<Dataset[]>('/datasets/')
      .then((res) => setDatasets(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { datasets, loading, error, refresh }
}
