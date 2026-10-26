import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

// Only the character is WebGL. The botanical SVG scene remains visible without it.
export default function VeritySphere({ paused }) {
  const canvasRef = useRef(null)
  const state = useRef({ paused })
  const wake = useRef(() => {})
  useEffect(() => {
    state.current = { paused }
    wake.current()
  }, [paused])

  useEffect(() => {
    const canvas = canvasRef.current
    let renderer
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' })
    } catch {
      return
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75))
    renderer.setClearColor(0x000000, 0)
    const scene = new THREE.Scene()
    const camera = new THREE.OrthographicCamera(-1.18, 1.18, 1.18, -1.18, .1, 10)
    camera.position.z = 5
    const character = new THREE.Group()
    scene.add(character)
    const sphereGeometry = new THREE.SphereGeometry(1, 64, 48)
    const sphereMaterial = new THREE.ShaderMaterial({
      vertexShader: `varying vec3 vNormal; varying vec3 vPosition;
        void main() { vNormal = normalize(normalMatrix * normal); vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `varying vec3 vNormal; varying vec3 vPosition;
        void main() {
          vec3 n = normalize(vNormal);
          float light = dot(n, normalize(vec3(-.55, .7, 1.0))) * .5 + .5;
          vec3 shadow = vec3(.93, .65, .09);
          vec3 sunlight = vec3(1.0, .88, .31);
          vec3 color = mix(shadow, sunlight, smoothstep(.05, 1.0, light));
          float grain = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898,78.233))) * 43758.5453);
          color += (grain - .5) * .026;
          gl_FragColor = vec4(color, 1.0);
        }`,
    })
    character.add(new THREE.Mesh(sphereGeometry, sphereMaterial))
    const ink = new THREE.MeshBasicMaterial({ color: '#252d20' })
    const eyeGeometry = new THREE.SphereGeometry(1, 24, 16)
    const leftEye = new THREE.Mesh(eyeGeometry, ink)
    const rightEye = new THREE.Mesh(eyeGeometry, ink)
    for (const [eye, x] of [[leftEye, -.29], [rightEye, .29]]) {
      eye.position.set(x, .16, .946)
      eye.scale.set(.065, .153, .025)
      character.add(eye)
    }
    const smilePoints = []
    for (let i = 0; i <= 40; i++) {
      const x = -.57 + i / 40 * 1.14
      const y = -.44 + .7 * x * x
      smilePoints.push(new THREE.Vector3(x, y, Math.sqrt(1 - x * x - y * y) + .013))
    }
    const smileCurve = new THREE.CatmullRomCurve3(smilePoints)
    const smileGeometry = new THREE.TubeGeometry(smileCurve, 64, .018, 8, false)
    character.add(new THREE.Mesh(smileGeometry, ink))
    const capGeometry = new THREE.SphereGeometry(.019, 12, 8)
    for (const point of [smilePoints[0], smilePoints[40]]) {
      const cap = new THREE.Mesh(capGeometry, ink)
      cap.position.copy(point)
      character.add(cap)
    }
    const pointer = { x: 0, y: 0 }
    const trackPointer = event => {
      pointer.x = (event.clientX / window.innerWidth - .5) * .14
      pointer.y = (.5 - event.clientY / window.innerHeight) * .09
    }
    const resetPointer = () => { pointer.x = 0; pointer.y = 0 }
    window.addEventListener('pointermove', trackPointer, { passive: true })
    document.addEventListener('pointerleave', resetPointer)
    let frame = 0
    let visible = true
    let disposed = false
    let elapsed = 0
    let lastTime = 0
    const render = now => {
      frame = 0
      if (disposed || !visible || document.hidden) return
      const dt = Math.min((now - lastTime) / 1000 || 0, .05)
      lastTime = now
      if (!state.current.paused) elapsed += dt
      const moving = !state.current.paused
      const targetX = moving ? pointer.y : 0
      const targetY = moving ? pointer.x : 0
      character.rotation.x += (targetX - character.rotation.x) * .045
      character.rotation.y += (targetY - character.rotation.y) * .045
      character.rotation.z = moving ? Math.sin(elapsed * .65) * .025 - .035 : -.035
      character.position.y = moving ? Math.sin(elapsed * 1.1) * .016 : 0
      renderer.render(scene, camera)
      canvas.classList.add('is-ready')
      if (moving) frame = requestAnimationFrame(render)
    }
    const start = () => {
      if (!frame && visible && !document.hidden && !disposed) {
        lastTime = performance.now()
        frame = requestAnimationFrame(render)
      }
    }
    wake.current = start
    const resize = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect
      if (width && height) {
        renderer.setSize(width, height, false)
        start()
      }
    })
    resize.observe(canvas)
    const intersection = new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting
      if (visible) start()
    }, { rootMargin: '80px' })
    intersection.observe(canvas)
    document.addEventListener('visibilitychange', start)
    const contextLost = event => {
      event.preventDefault()
      canvas.classList.remove('is-ready')
      cancelAnimationFrame(frame)
      frame = 0
    }
    canvas.addEventListener('webglcontextlost', contextLost)
    canvas.addEventListener('webglcontextrestored', start)
    start()
    return () => {
      disposed = true
      wake.current = () => {}
      cancelAnimationFrame(frame)
      resize.disconnect()
      intersection.disconnect()
      window.removeEventListener('pointermove', trackPointer)
      document.removeEventListener('pointerleave', resetPointer)
      document.removeEventListener('visibilitychange', start)
      canvas.removeEventListener('webglcontextlost', contextLost)
      canvas.removeEventListener('webglcontextrestored', start)
      for (const resource of [sphereGeometry, sphereMaterial, ink, eyeGeometry, smileGeometry, capGeometry]) resource.dispose()
      renderer.dispose()
    }
  }, [])

  return <canvas ref={canvasRef} className="sphere-canvas" aria-hidden="true" />
}
