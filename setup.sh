#!/usr/bin/env bash
# Installs Blender-as-a-module and the MPFB (MakeHuman for Blender) extension it uses to build the bodies.
set -euo pipefail
MPFB_REF=${MPFB_REF:-3af0cd5a2ffba072e93a34e5f6f494fdc4813ddf}
python3 -m pip install --quiet "bpy==5.2.2" pillow
if [ ! -d .mpfb2 ]; then
  git clone --quiet https://github.com/makehumancommunity/mpfb2 .mpfb2
  git -C .mpfb2 checkout --quiet "$MPFB_REF"
fi
EXT=$(python3 -c "import bpy;print(bpy.utils.user_resource('EXTENSIONS', path='user_default'))" 2>/dev/null | tail -1)
mkdir -p "$EXT"
ln -sfn "$PWD/.mpfb2/src/mpfb" "$EXT/mpfb"
echo "MPFB linked into $EXT"
