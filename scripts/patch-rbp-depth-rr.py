#!/usr/bin/env python3
"""
    ------------------- Ganpati Bappa Morya -----------------
Set XDJ-RR rbp's layer pixel format — the third and last patch stage.

Stock XDJ-RR rbp hardcodes one DirectFB layer format in
DS_HW_Core_Layer_Create (VA 0x001583D4), and on this port that single word
is the difference between 16 bpp and 32 bpp rendering.

    0x00200801  DSPF_RGB16   the XDJ-RR's own framebuffer, and what stock asks for
    0x00400c03  DSPF_RGB32   the handoff's format, and the one that draws the
                             edge whole

Two instructions carry it — `movw r3,#0x801` / `movt r3,#0x20` for 16, and
`movw r3,#0xc03` / `movt r3,#0x40` for 32 — so changing the depth is two words,
eight bytes, and nothing else in the function moves.

THIS IS HALF OF A PAIR, AND THE HALF THAT CANNOT SEE THE OTHER. The shim lies to
rbp and to DirectFB about the framebuffer's depth through FBIOGET_VSCREENINFO
(scripts/shims/fb_shim.c's fb_lie_bpp(), fed by rb.conf's RB_FB_LIE_BPP). The two
must agree:

  * the shim says 32 and this word says 16 -> DirectFB's real fbdev driver is
    handed a 16-bpp layer request against the 32-bpp var the shim reports, its
    DS_HW layer plugin refuses, and rbp segfaults before the panel opens: black
    screen, systemd restart-looping, no log line that names the cause.
  * the shim says 16 and this word says 32 -> the mirror of the same refusal.

So the depth is not this script's choice to make. build-chroot.sh reads
RB_FB_LIE_BPP out of the very rb.conf it embeds and passes it here, and
start-rb.sh re-checks the pair at launch.

Idempotent in both directions, and it validates the word it finds at every
address, so it cannot corrupt a foreign binary — it aborts instead.

Usage:
    python3 patch-rbp-depth-rr.py rbp-rr-step1                    # -> 32 bpp, in place
    python3 patch-rbp-depth-rr.py rbp-rr-step1 -o rbp-rr-step2    # -> 32 bpp, new file
    python3 patch-rbp-depth-rr.py rbp-rr-step2 --bpp 16           # -> back to 16 bpp
    python3 patch-rbp-depth-rr.py rbp-rr-step1 --check

    --bpp N   the depth to write (default 32). Passing 16 reverts.
    --check   report the depth each address currently holds; write nothing.
"""

import argparse
import hashlib
import os
import struct
import sys

# (file_offset, word_at_16bpp, word_at_32bpp, note)
#
# Both words are hand-checked against the port's own two builds rather than
# derived: `.239` runs the 32 pair (md5 990404244853a7d613be3d469ad1bc1d) and
# `work/patched` holds the 16 pair, and the two differ in exactly these 8 bytes.
# VA maps to file_offset = VA - 0x8000 (non-PIE ARM32 ELF), so 0x1a3ab8 in the
# disassembly is 0x19bab8 here.
WORDS = [
    (0x1503F8, 0xE3003801, 0xE3003C03, "movw r3, #0x801 (DSPF_RGB16) <-> #0xc03 (DSPF_RGB32)"), # RR (RX3: 0x19BAB8, 0xE3003801)
    (0x150400, 0xE3403020, 0xE3403040, "movt r3, #0x20                <-> #0x40"),              # RR (RX3: 0x19BAC0, 0xE3403020)
]

DEPTH_TO_WORDS = {16: 1, 32: 2}          # index into each tuple: 1 = 16 bpp, 2 = 32 bpp
DEPTH_OF_BYTE = {0x01: 16, 0x03: 32}     # the low byte at the first offset

# The single byte `start-rb.sh` reads to make the same call on the unit. Stated
# here so the launcher's shell arithmetic and this file's table cannot drift.
PROBE_OFFSET = WORDS[0][0]


def check_size(data):
    """A truncated or foreign file would otherwise die in struct.unpack_from with
    a bare traceback, which reads as a bug in the patcher rather than 'wrong
    input file'."""
    need = max(off for off, _, _, _ in WORDS) + 4
    if len(data) < need:
        raise SystemExit(
            f"  {len(data)} bytes is too short: the patch table needs at least "
            f"{need}. This is not the XDJ-RX3 rbp binary."
        )


def current_depth(data):
    """16, 32, or None when the word at PROBE_OFFSET is neither — a stock or
    foreign binary, or one carrying a depth nothing here knows how to name."""
    return DEPTH_OF_BYTE.get(data[PROBE_OFFSET])


def apply(data, depth):
    """Write the word pair for `depth`. Each address is validated first, and a
    word that is neither the 16 nor the 32 value aborts rather than being
    overwritten -- this is the only thing standing between a wrong file and a
    silently corrupted player."""
    for off, w16, w32, note in WORDS:
        want = w16 if depth == 16 else w32
        other = w32 if depth == 16 else w16
        cur = struct.unpack_from("<I", data, off)[0]
        if cur == want:
            print(f"  {off:#08x}: already {depth} bpp ({note})")
        elif cur == other:
            struct.pack_into("<I", data, off, want)
            print(f"  {off:#08x}: {cur:#010x} -> {want:#010x}  ({note})")
        else:
            raise SystemExit(
                f"  {off:#08x}: expected {w16:#010x} (16 bpp) or {w32:#010x} "
                f"(32 bpp), found {cur:#010x} — wrong/foreign binary?"
            )


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("input")
    ap.add_argument("-o", "--output",
                    help="output path (default: the input, replaced atomically)")
    ap.add_argument("--bpp", type=int, choices=(16, 32), default=32,
                    help="the depth to write (default: 32)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    with open(args.input, "rb") as f:
        data = bytearray(f.read())

    check_size(data)

    if args.check:
        found = current_depth(data)
        for off, w16, w32, note in WORDS:
            cur = struct.unpack_from("<I", data, off)[0]
            status = ("16 bpp" if cur == w16 else "32 bpp" if cur == w32
                      else "UNKNOWN")
            print(f"  {off:#08x}: {cur:#010x}  {status}  ({note})")
        print(f"  renders at {found} bpp (asked for {args.bpp})" if found
              else "  not a recognised depth — not a build this tree produced")
        return 0

    print(f"patching {args.input} ({len(data)} bytes) -> {args.bpp} bpp")
    print(f"in  {hashlib.md5(bytes(data)).hexdigest()}")
    apply(data, args.bpp)

    out = args.output
    if out:
        with open(out, "wb") as f:
            f.write(data)
        print(f"wrote {out}")
    else:
        # In place, and by a rename rather than an open(O_TRUNC) on the target:
        # the same rule the launcher and install.sh follow for anything a running
        # player may have mapped. A build script has no live rbp to worry about,
        # but a half-written player after an ENOSPC is not worth the two lines it
        # saves to skip this.
        tmp = args.input + ".depth.tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, args.input)
        print(f"wrote {args.input} (in place)")
    print(f"out {hashlib.md5(bytes(data)).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
