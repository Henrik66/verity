import React from 'react'
import Garden, { useMediaQuery } from './Garden.jsx'

export default function App() {
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')
  return <main className="garden-page" aria-label="Verity garden">
    <Garden reducedMotion={reducedMotion} />
  </main>
}
