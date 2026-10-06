#!/bin/sh -e

# Images are at https://winworldpc.com/product/ms-dos/622

# Microsoft MS-DOS 6.22 with CD-Rom Support [Virtual PC VHD]
# mirrors
# https://winworldpc.com/download/3dc392c3-b845-18c3-9a11-c3a4e284a2ef/from/c39ac2af-c381-c2bf-1b25-11c3a4e284a2
# https://winworldpc.com/download/3dc392c3-b845-18c3-9a11-c3a4e284a2ef/from/c3ae6ee2-8099-713d-3411-c3a6e280947e

url="https://winworldpc.com/download/3dc392c3-b845-18c3-9a11-c3a4e284a2ef/from/c3ae6ee2-8099-713d-3411-c3a6e280947e"

# Download the file and capture the final filename into a variable
f=$(curl -LOJ -w "%{filename_effective}" $url)
f7z=ms-dos-622.7z
echo "downloaded $f"
mv -v "$f" "$f7z"
file "$f7z"
7z x "$f7z" 

mv -v Microsoft\ MS-DOS\ 6.22\ with\ CD-Rom\ Support\ VHD/MS-DOS\ 6.22\ with\ CD-Rom\ Support\ VHD.vhd ./ms-dos-622.vhd
file ms-dos-622.vhd
qemu-img convert -O raw ms-dos-622.vhd ms-dos-622.raw
file ms-dos-622.raw
