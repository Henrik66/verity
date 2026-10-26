# Verity garden

The supplied smiley-in-a-meadow image is the visual reference for this frontend.
The current request is for a working React frontend with a smiling sphere,
wind-driven plants, and clouds moving behind the character.

- Sky: `#8fc7df` to `#a7d5e6`, open and lightly grained.
- Clouds / petals: `#f4f2df`, warm rather than pure white.
- Distant hills: `#a1c6b5`, `#96bca2`, `#88aa80`.
- Foliage: `#315d46`, `#3f7050`, `#547e49`, `#719448`, `#84a34e`.
- Character: sunflower yellow, shaded from `#edA617` to `#ffe050`.
- Ink: `#243e30`. Below-the-fold paper: `#f7f6ec`.
- Type: none in the current scene. The user requested all visible text be removed.
- Drawing: filled, irregular botanical silhouettes; curved stems; no black
  outlines on the garden. Broad leaves, grass, clover, daisies, and buttercups.
- Face: original yellow sphere, two narrow oval eyes, a simple curved smile.
- Composition: large open sky above a dense layered meadow; character centered
  and partly hidden behind the nearest leaves. The sky remains open.
- Motion: low-amplitude plant sway with different phases, slower clouds behind
  the plants, very subtle character movement. Reduced-motion support. The face
  holds a steady smile, with no wink or blink.
- Raster texture and impossible overlapping shapes in the reference are mood
  cues, not exact geometry.

The garden is drawn in SVG for editability; only the sphere uses Three.js.
