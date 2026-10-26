import React, { lazy, memo, Suspense, useEffect, useState } from 'react'

const VeritySphere = lazy(() => import('./VeritySphere.jsx'))

export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches)
  useEffect(() => {
    const media = window.matchMedia(query)
    const update = () => setMatches(media.matches)
    update()
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [query])
  return matches
}

export function Smiley({ className = '', ...props }) {
  return <svg viewBox="0 0 100 100" className={className} {...props}>
    <circle cx="50" cy="50" r="48" fill="currentColor" />
    <g fill="#233b2a"><ellipse cx="35" cy="41" rx="4.1" ry="7.5" /><ellipse cx="65" cy="41" rx="4.1" ry="7.5" /></g>
    <path d="M25 57 C35 78 66 78 77 55" fill="none" stroke="#233b2a" strokeWidth="4" strokeLinecap="round" />
  </svg>
}

function random(seed) {
  return () => {
    seed |= 0
    seed = seed + 0x6D2B79F5 | 0
    let n = Math.imul(seed ^ seed >>> 15, 1 | seed)
    n = n + Math.imul(n ^ n >>> 7, 61 | n) ^ n
    return ((n ^ n >>> 14) >>> 0) / 4294967296
  }
}

function PlantDefinitions() {
  return <svg width="0" height="0" className="plant-defs" aria-hidden="true"><defs>
    <path id="leaf-lance" d="M0 0 C9 -17 17 -35 43 -44 C41 -24 31 -7 0 0Z" />
    <path id="leaf-round" d="M0 0 C6 -9 2 -20 13 -24 C20 -31 34 -27 42 -35 C47 -23 35 -4 24 -3 C14 2 7 -2 0 0Z" />
    <path id="leaf-nettle" d="M0 0 L5 -9 5 -15 12 -15 12 -23 20 -24 20 -29 29 -29 32 -34 43 -35 43 -27 40 -22 39 -16 32 -14 30 -8 23 -8 20 -2 12 -3 9 0Z" />
    <path id="grass-blade" d="M-5 0 C-9 -49 13 -115 57 -155 C27 -110 10 -48 8 0Z" />
    <g id="clover-leaf"><path d="M0 0 C-14 -3 -19 -15 -11 -19 C-18 -28 -3 -33 1 -25 C8 -37 20 -27 16 -20 C29 -17 23 -5 14 -6 C16 4 5 7 0 0Z" /></g>
    <g id="daisy-head">
      {[0, 72, 144, 216, 288].map(angle => <ellipse key={angle} cx="0" cy="-8" rx="5.8" ry="9" transform={`rotate(${angle})`} fill="#f6f3d9" />)}
      <circle r="4.7" fill="#eac85e" />
    </g>
    <g id="buttercup-head"><path d="M0 0 C-14 -3 -16 -13 -9 -15 C-9 -24 3 -27 7 -18 C17 -20 23 -10 15 -5 C19 4 7 8 0 0Z" fill="#e9c849" /></g>
  </defs></svg>
}

function Stem({ height, kind, flip, seed }) {
  const rng = random(seed)
  const lean = (rng() - .5) * height * .35
  if (kind === 'grass') return <g>
    {[0, 1, 2].map(i => <use key={i} href="#grass-blade" transform={`rotate(${(i - 1) * 32 + flip * 9}) scale(${height / 155 * (.65 + i * .16)})`} />)}
  </g>
  const flower = kind === 'daisy' || kind === 'buttercup'
  const count = flower ? 4 : 7
  const leaf = kind === 'fern' ? 'leaf-lance' : kind === 'clover' ? 'clover-leaf' : seed % 2 === 0 ? 'leaf-nettle' : 'leaf-round'
  return <g>
    <path d={`M0 0 Q${lean * .3} ${-height * .5} ${lean} ${-height}`} fill="none" stroke="currentColor" strokeWidth={flower ? 2.8 : 3.1} strokeLinecap="round" />
    {Array.from({ length: count }, (_, i) => {
      const t = (i + 1) / (count + 1)
      const side = i % 2 ? 1 : -1
      const scale = (height / 130) * (.85 - t * .32) * (flower ? .55 : 1)
      return <use key={i} href={`#${leaf}`} transform={`translate(${lean * t * t}, ${-height * t}) rotate(${side * (rng() * 16 - 4)}) scale(${side * scale}, ${scale})`} />
    })}
    {flower ? <g transform={`translate(${lean} ${-height})`}>
      <use href={`#${kind}-head`} transform={`scale(${kind === 'daisy' ? .85 : .65}) rotate(${flip * 20})`} />
      {kind === 'buttercup' && <>
        <path d="M0 24 Q-19 12 -20 -5 M-1 42 Q17 26 18 11" fill="none" stroke="currentColor" strokeWidth="2.5" />
        <use href="#buttercup-head" transform="translate(-20 -5) scale(.48)" />
        <use href="#buttercup-head" transform="translate(18 11) scale(.55)" />
      </>}
    </g> : <use href={`#${leaf}`} transform={`translate(${lean} ${-height + 10}) rotate(-30) scale(.6)`} />}
  </g>
}

const PlantLayer = memo(function PlantLayer({ layer, mobile }) {
  const width = mobile ? 600 : 1600
  const rng = random(layer === 'back' ? 124 : 769)
  const back = layer === 'back'
  const count = mobile ? (back ? 65 : 48) : (back ? 155 : 105)
  const colors = back ? ['#719958', '#85a85e', '#608b57', '#769b58', '#4f8059'] : ['#315d46', '#3f7050', '#547e49', '#719448', '#456d43', '#84a34e']
  const plants = Array.from({ length: count }, (_, i) => {
    const x = rng() * (width + 100) - 50
    const edge = Math.abs(x - width / 2) / (width / 2)
    const clearCenter = Math.max(0, 1 - edge / .32)
    const y = back ? 420 + rng() * 150 : 515 + rng() * 150 + clearCenter * 42
    const height = back ? 50 + rng() * 95 + edge * 80 : (65 + rng() * 110 + Math.pow(edge, 1.4) * 170) * (1 - clearCenter * .33)
    const kinds = ['foliage', 'foliage', 'grass', 'clover', 'fern', 'daisy', 'buttercup']
    const kind = kinds[Math.floor(rng() * kinds.length)]
    return { x, y, height, kind, color: colors[Math.floor(rng() * colors.length)], flip: rng() > .5 ? 1 : -1, duration: 4 + rng() * 4, delay: -rng() * 10, angle: (rng() - .5) * 32, seed: i + (back ? 567 : 123) }
  }).sort((a, b) => a.y - b.y)
  return <svg className={`botanical-layer botanical-${layer}`} viewBox={`0 0 ${width} 650`} preserveAspectRatio="xMidYMax slice" aria-hidden="true">
    {back && <path d={`M-10 480 Q${width * .23} 400 ${width * .5} 480 Q${width * .8} 410 ${width + 10} 450 V660 H-10Z`} fill="#779a60" />}
    {!back && <path d={`M-10 600 Q${width * .25} 510 ${width * .5} 600 Q${width * .8} 540 ${width + 10} 570 V660 H-10Z`} fill="#3b6548" />}
    {plants.map((p, i) => <g key={i} transform={`translate(${p.x} ${p.y}) rotate(${p.angle})`} color={p.color} fill={p.color}>
      <g className="plant" style={{ '--sway': `${p.kind === 'grass' ? 4 : 2.4}deg`, animationDuration: `${p.duration}s`, animationDelay: `${p.delay}s` }}>
        <Stem {...p} />
      </g>
    </g>)}
  </svg>
})

export default function Garden({ reducedMotion }) {
  const mobile = useMediaQuery('(max-width: 600px)')
  return <div className={`garden-scene ${reducedMotion ? 'is-still' : ''}`} role="img" aria-label="Verity, a smiling yellow sphere surrounded by gently swaying plants and drifting clouds.">
    <PlantDefinitions />
    <div className="sky-grain" aria-hidden="true" />
    <svg className="cloud cloud-left" viewBox="0 0 800 300" aria-hidden="true"><path d="M-20 285 V111 C2 73 43 75 65 99 C55 45 109 6 151 32 C184 -16 258 7 260 65 C311 41 366 88 347 134 C384 113 429 145 425 180 C476 157 518 177 532 216 C589 204 602 246 645 246 C715 232 759 262 820 275 V310Z" fill="#f4f2df" /></svg>
    <svg className="cloud cloud-right" viewBox="0 0 800 300" aria-hidden="true"><path d="M-20 285 C27 252 80 277 119 243 C166 208 200 236 227 220 C243 179 286 174 313 186 C326 138 369 115 413 135 C419 82 465 63 504 85 C488 35 542 -2 585 20 C640 -28 708 16 701 74 C760 58 787 113 815 153 V310 H-20Z" fill="#f4f2df" /></svg>
    <svg className="distant-hills" viewBox="0 0 1600 300" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 85 Q130 34 320 100 T640 108 T960 80 T1280 103 T1600 55 V300 H0Z" fill="#a1c6b5" />
      <path d="M0 137 Q210 72 410 150 T800 131 T1200 150 T1600 99 V300 H0Z" fill="#96bca2" />
      <path d="M0 210 Q210 122 500 196 T1000 175 T1600 173 V300 H0Z" fill="#88aa80" />
    </svg>
    <PlantLayer layer="back" mobile={mobile} />
    <div className="verity-character" aria-hidden="true">
      <span className="sphere-fallback"><Smiley aria-hidden="true" /></span>
      <Suspense fallback={null}><VeritySphere paused={reducedMotion} /></Suspense>
    </div>
    <PlantLayer layer="front" mobile={mobile} />
    <div className="garden-shade" aria-hidden="true" />
  </div>
}
