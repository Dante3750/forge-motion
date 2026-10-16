# Forge Motion

| Gym | Home · dumbbells | No equipment |
|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/Dante3750/forge-motion/media/showcase/hero_gym.gif" width="100%"> | <img src="https://raw.githubusercontent.com/Dante3750/forge-motion/media/showcase/hero_home.gif" width="100%"> | <img src="https://raw.githubusercontent.com/Dante3750/forge-motion/media/showcase/hero_bodyweight.gif" width="100%"> |

Two camera angles for every movement:

<img src="https://raw.githubusercontent.com/Dante3750/forge-motion/media/showcase/hero_angles.gif" width="420">

3D human workout loops for the [Forge gym app](https://github.com/Dante3750/forge-gym), rendered from code with free tools.

Every movement (squat, bench press, pull-up, plank, stretches and more — 101 in total, with gym, home-dumbbell and bodyweight versions) is written as a few key poses in
[`render/patterns.py`](render/patterns.py). A male and a female body are generated with MakeHuman, posed by a small
joint-target solver ([`render/poser.py`](render/poser.py), [`render/body.py`](render/body.py)), dressed and lit in
[`render/scene.py`](render/scene.py), and rendered with Blender Cycles. Every one of the 876 exercises in the app maps to
the closest movement in [`render/map.json`](render/map.json) (built by [`render/mapper.py`](render/mapper.py)).

## Every movement

<img src="https://raw.githubusercontent.com/Dante3750/forge-motion/media/showcase/gallery.jpg" width="100%">

The previews and gallery are rebuilt by the **Showcase** workflow after every render.

## How it runs

The **Render movements** GitHub Action renders everything in 20 parallel jobs and publishes the results to the
`media` branch:

- `v3/<movement>_<m|f>[_b]_0.webp`, `_1.webp` — HD sprite sheets, 32 frames of 640×640 (4×4 per sheet), auto-framed
- `v3/<movement>_<m|f>[_b]_s.webp` — small sheet (200px frames) for thumbnails
- `v3/<movement>_<m|f>.preview.webp` — small animated preview
- `v3/index.json` — frame layout for every loop
- `v3/map.json` — exercise id → movement

Run it again from the Actions tab (optionally for just a few movements) after changing a pose.

## Run locally

```bash
./setup.sh                                                  # Blender as a Python module + MPFB
python3 render/render_one.py squat_bb m out/squat 32 400 28 # one loop
python3 render/pack.py out/squat sheets squat_bb_m          # sprite sheet + preview
```

## Credits

- Human bodies, rig and eyes: [MakeHuman](http://www.makehumancommunity.org/) assets, CC0.
- Body generation: [MPFB](https://github.com/makehumancommunity/mpfb2), used as a build tool (GPL, not redistributed here).
- Renderer: [Blender](https://www.blender.org/) (`bpy` from PyPI).

The rendered images are released under CC0.
