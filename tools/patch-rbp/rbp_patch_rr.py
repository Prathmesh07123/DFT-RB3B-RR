#!/usr/bin/env python3
"""
 ------------------- Ganpati Bappa Morya --------------------
rbp_patch_rr.py - apply the interoperability patches to a stock
XDJ-RR `rbp` binary for running on Raspberry Pi 3B.

Based on the XDJ-RX3 rbp_patch.py table, with all addresses
re-discovered in the XDJ-RR rbp binary.

Usage:
    python3 rbp_patch_rr.py <stock-rbp-rr> [-o rbp-rr-patched] [--check]

Notes:
    * rbp is a non-PIE ARM32 ELF.  virtual address (VA) = file offset + 0x8000.
    * The patcher is idempotent: running it on an already-patched binary is a
      no-op ("already patched") and never double-applies.
    * Every patch records the expected *stock* word so a wrong/foreign binary
      is rejected instead of corrupted.
"""
import argparse
import struct
import sys

LOAD_BIAS = 0x8000

# (VA, stock_word, patched_word, note)
PATCHES = [
    # --- base USB / browse / panel / startup fixes ("rbp-dbsfix" lineage) ---
    (0x00022854, 0x0A000021, 0xE1000000, "dbsfix: short-circuit vendor startup check"),          # RR (RX3: 0x020AF0, 0x0A000022)
    (0x00022860, 0xEB038426, 0xE1000000, "dbsfix: short-circuit vendor startup call"),           # RR (RX3: 0x020AFC, 0xEB0490F4)
    (0x0002286C, 0x0A000012, 0xE1000000, "dbsfix: short-circuit vendor startup branch"),         # RR (RX3: 0x020B08, 0x0A000013)
    (0x000229B4, 0x003A6114, 0x64656D2F, "dbsfix: '/media/usb1/sda1' mount path string (1/5)"),  # RR (RX3: 0x020C54, 0x003FE218) RISKY
    (0x000229B8, 0x016BE618, 0x752F6169, "dbsfix: mount path string (2/5)"),                     # RR (RX3: 0x020C58, 0x02435738) RISKY
    (0x000229BC, 0x016BE4C8, 0x2F316273, "dbsfix: mount path string (3/5)"),                     # RR (RX3: 0x020C5C, 0x024355E8) RISKY
    (0x000229C0, 0x0047EB98, 0x31616473, "dbsfix: mount path string (4/5)"),                     # RR (RX3: 0x020C60, 0x004E3054) RISKY
    (0x000229C4, 0x0047EB88, 0x004D5200, "dbsfix: mount path string (5/5)"),                     # RR (RX3: 0x020C64, 0x004D52C0) RISKY
    (0x00117F88, 0xE5C8300F, 0xE320F000, "dbsfix: NOP vendor status write"),                     # RR (RX3: 0x159CE8, 0xE5C9300F)
    (0x00234888, 0x012FFF1E, 0xE1A00000, "touch A/F: IReceptionForMAIN::startUp never early-returns"),  # RR (RX3: 0x2BB87C, 0x012FFF1E)
    (0x0024D7F4, 0x18BD8038, 0xE1A00000, "touch D: TouchPanel::openDevice never bails"),         # RR (RX3: 0x2D6CB0, 0x18BD8038)
    (0x0028D174, 0x1A000010, 0xE1A00000, "touch E: startUp never bails on panel flag"),          # RR (RX3: 0x31DDB0, 0x1A000014)
    (0x0028D17C, 0x0A00000A, 0xEAFFFFFF, "touch B: startUp skips failing internal init"),        # RR (RX3: 0x31DDB8, 0x0A00000E)
    (0x002C8E9C, 0x1A000004, 0xEA000004, "touch G: PanelComPeerLinux::postMessage deadlock fix"),# RR (RX3: 0x366530, 0x1A000004)

    # --- code cave used by the browse/USB routing patches ---
    (0x00075870, 0x00000000, 0xE3A01000, "usb: code cave (mov r1,#0)"),                          # RR (RX3: 0x09B678, 0x00000000) VERIFY
    (0x00075874, 0x00000000, 0xEA0B8337, "usb: code cave branch -> setBrowseMode(12)"),          # RR (RX3: 0x09B67C, 0x00000000) VERIFY

    # --- key dispatch / throw-hardening ("rbp-fixthrow" lineage) ---
    (0x002474D8, 0xE3A00004, 0xE8BD8070, "fixthrow: UiTimer throw path -> pop/return"),          # RR (RX3: 0x2CF7A0, 0xE3A00004)
    (0x002C963C, 0xE3A01002, 0xE3001802, "fixthrow: socketpair() non-blocking"),                 # RR (RX3: 0x366CD0, 0xE3A01002)
    (0x002DCB54, 0xE92D4FF0, 0xE12FFF1E, "notimer: UiTimer callback -> immediate return (bx lr)"), # RR (RX3: 0x3779C0, 0xE92D4FF8)
    (0x002EE6EC, 0x0A00014B, 0x0A000007, "fixthrow: KeyInput dispatch slot search (1/3)"),       # RR (RX3: 0x37AD90, 0x0A00014B)
    (0x002EE6F0, 0xE5900004, 0xEA000019, "fixthrow: KeyInput dispatch slot search (2/3)"),       # RR (RX3: 0x37AD94, 0xE5900004)
    (0x002EE70C, 0x1A000012, 0xEA000012, "fixthrow: KeyInput dispatch slot search (3/3)"),       # RR (RX3: 0x37ADB0, 0x1A000012)
    (0x002EF448, 0xAA0002F0, 0xE320F000, "fixthrow: IKeyInput bounds check NOP"),                # RR (RX3: 0x37B5D0, 0xAA0002AB)
    (0x002EFB00, 0xAA0000DD, 0xEAFFFFF8, "fixthrow: FixedAddressArray::add throw -> skip"),      # RR (RX3: 0x37BC30, 0xAA0000CC)
    (0x002EFB08, 0xDA0000DB, 0xEAFFFFF6, "fixthrow: FixedAddressArray::add throw -> skip"),      # RR (RX3: 0x37BC38, 0xDA0000CA)
    (0x002EFE48, 0xDA00000B, 0xEA000052, "fixthrow: FixedAddressArray bounds -> no-throw path"), # RR (RX3: 0x37BF34, 0xDA00000B) VERIFY
    (0x002EFE7C, 0xE3A00004, 0xEAF47DC2, "fixthrow: return no-free-slot via cave"),              # RR (RX3: 0x37BF68, 0xE3A00004)
    (0x002EFFD4, 0xAA00000D, 0xE320F000, "fixthrow: key-target array bound NOP"),                # RR (RX3: 0x37C048, 0xAA00000D)
    (0x002EFFDC, 0xDA00000B, 0xE320F000, "fixthrow: key-target array bound NOP"),                # RR (RX3: 0x37C050, 0xDA00000B)
    (0x002F0010, 0xE3A00004, 0xEAF47D7B, "fixthrow: return no-free-slot via cave"),              # RR (RX3: 0x37C084, 0xE3A00004)
    (0x002F04CC, 0x0AFFFECF, 0xE320F000, "fixthrow: key-target removal guard NOP"),              # RR (RX3: 0x37C364, 0x0AFFFF46)
    (0x002F0A3C, 0xE58450A4, 0xE58480A4, "fixthrow: KeyManager pending-bitmask init"),           # RR (RX3: 0x37C710, 0xE58450A4)

    # --- power-manager NULL-this guards (no Pioneer PM hardware) ---
    (0x000EEB2C, 0xE92D41F0, 0xE3A00000, "pm: IPowerManager helper -> mov r0,#0"),               # RR (RX3: 0x121D9C, 0xE92D41F0)
    (0x000EEB30, 0xEB013B84, 0xE12FFF1E, "pm: IPowerManager helper -> bx lr"),                   # RR (RX3: 0x121DA0, 0xEB01955A)
    (0x000EEC04, 0xE92D4038, 0xE3A00000, "pm: IPowerManager helper -> mov r0,#0"),               # RR (RX3: 0x12203C, 0xE92D4038)
    (0x000EEC08, 0xEB013B4E, 0xE12FFF1E, "pm: IPowerManager helper -> bx lr"),                   # RR (RX3: 0x122040, 0xEB0194B2)
    (0x000EEC40, 0xE92D45F0, 0xE3A00000, "pm: IPowerManager helper -> mov r0,#0"),               # RR (RX3: 0x122078, 0xE92D45F0)
    (0x000EEC44, 0xE24DD00C, 0xE12FFF1E, "pm: IPowerManager helper -> bx lr"),                   # RR (RX3: 0x12207C, 0xE24DD00C)
    (0x00241DF8, 0xE92D4038, 0xE12FFF1E, "pm: notifyPermissionChanged -> bx lr (NULL this)"),    # RR (RX3: 0x2C6BF0, 0xE92D4038)
    (0x0024220C, 0xE92D4070, 0xE12FFF1E, "pm: notifyPreparedToStandby -> bx lr (NULL this)"),    # RR (RX3: 0x2C7004, 0xE92D4070)
    (0x002AD4D8, 0xE92D45F8, 0xE12FFF1E, "pm: USB/power notification helper -> bx lr"),          # RR (RX3: 0x32E728, 0xE92D45F8)
    (0x002F95A0, 0xE1A00006, 0xE3A00000, "pm: notification helper -> mov r0,#0"),                # RR (RX3: 0x3871D0, 0xE1A00006)

    # --- touch: caution gate ---
    (0x00251B38, 0xE1A07000, 0xE3A07000, "touch: solveCoordToKey ignores caution id"),           # RR (RX3: 0x2DC228, 0xE1A07000)
    (0x00251BF0, 0x0A000009, 0xEA000009, "touch: touchOn bypasses caution check"),               # RR (RX3: 0x2DC46C, 0x0A000008)

    # --- panel / comm helpers ---
    (0x002C8E20, 0xE0633000, 0xE3A03000, "panel: comm helper -> r3 = 0"),                        # RR (RX3: 0x3664B4, 0xE0633000)

    # --- audio: force RX3 device list on non-i.MX6 CPU ---
    (0x0034CD50, 0x1A00004F, 0xEA00004F, "audio: ALSAAudioIODeviceType::scanForDevices force RX3 list"), # RR (RX3: 0x3C665C, 0x1A000054)

    # --- udev FIFO paths: /proc/udev_* -> /tmp/udev_* ---
    (0x004792B4, 0x6F72702F, 0x706D742F, "udev: '/proc/udev_usb1' -> '/tmp/udev_usb1' (1/4)"),   # RR (RX3: 0x4DEDE4, 0x6F72702F)
    (0x004792B8, 0x64752F63, 0x6564752F, "udev: usb1 path (2/4)"),                               # RR (RX3: 0x4DEDE8, 0x64752F63)
    (0x004792BC, 0x755F7665, 0x73755F76, "udev: usb1 path (3/4)"),                               # RR (RX3: 0x4DEDEC, 0x755F7665)
    (0x004792C0, 0x00316273, 0x00003162, "udev: usb1 path (4/4)"),                               # RR (RX3: 0x4DEDF0, 0x00316273)
    (0x004792C4, 0x6F72702F, 0x706D742F, "udev: '/proc/udev_usb2' -> '/tmp/udev_usb2' (1/4)"),   # RR (RX3: 0x4DEDF4, 0x6F72702F)
    (0x004792C8, 0x64752F63, 0x6564752F, "udev: usb2 path (2/4)"),                               # RR (RX3: 0x4DEDF8, 0x64752F63)
    (0x004792CC, 0x755F7665, 0x73755F76, "udev: usb2 path (3/4)"),                               # RR (RX3: 0x4DEDFC, 0x755F7665)
    (0x004792D0, 0x00326273, 0x00003262, "udev: usb2 path (4/4)"),                               # RR (RX3: 0x4DEE00, 0x00326273)
    (0x0047C9E4, 0x6F72702F, 0x706D742F, "udev: '/proc/udev_usbctn1' -> '/tmp/udev_usbctn1' (1/5)"), # RR (RX3: 0x4E0E54, 0x6F72702F)
    (0x0047C9E8, 0x64752F63, 0x6564752F, "udev: ctn1 path (2/5)"),                               # RR (RX3: 0x4E0E58, 0x64752F63)
    (0x0047C9EC, 0x755F7665, 0x73755F76, "udev: ctn1 path (3/5)"),                               # RR (RX3: 0x4E0E5C, 0x755F7665)
    (0x0047C9F0, 0x74636273, 0x6E746362, "udev: ctn1 path (4/5)"),                               # RR (RX3: 0x4E0E60, 0x74636273)
    (0x0047C9F4, 0x0000316E, 0x00000031, "udev: ctn1 path (5/5)"),                               # RR (RX3: 0x4E0E64, 0x0000316E)
    (0x0047C9F8, 0x6F72702F, 0x706D742F, "udev: '/proc/udev_usbctn2' -> '/tmp/udev_usbctn2' (1/5)"), # RR (RX3: 0x4E0E68, 0x6F72702F)
    (0x0047C9FC, 0x64752F63, 0x6564752F, "udev: ctn2 path (2/5)"),                               # RR (RX3: 0x4E0E6C, 0x64752F63)
    (0x0047CA00, 0x755F7665, 0x73755F76, "udev: ctn2 path (3/5)"),                               # RR (RX3: 0x4E0E70, 0x755F7665)
    (0x0047CA04, 0x74636273, 0x6E746362, "udev: ctn2 path (4/5)"),                               # RR (RX3: 0x4E0E74, 0x74636273)
    (0x0047CA08, 0x0000326E, 0x00000032, "udev: ctn2 path (5/5)"),                               # RR (RX3: 0x4E0E78, 0x0000326E)
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rbp", help="stock XDJ-RR rbp binary")
    ap.add_argument("-o", "--output", default="rbp-rr-patched",
                    help="output path (default: rbp-rr-patched)")
    ap.add_argument("--check", action="store_true",
                    help="verify only, do not write anything")
    args = ap.parse_args()

    with open(args.rbp, "rb") as fh:
        data = bytearray(fh.read())

    applied = already = 0
    for va, old, new, note in PATCHES:
        off = va - LOAD_BIAS
        if off < 0 or off + 4 > len(data):
            print(f"  !! VA 0x{va:06X} outside file", file=sys.stderr)
            return 2
        cur = struct.unpack_from("<I", data, off)[0]
        if cur == new:
            already += 1
            continue
        if cur != old:
            print(f"  !! mismatch at VA 0x{va:06X}: expected 0x{old:08X}, "
                  f"found 0x{cur:08X}  ({note})", file=sys.stderr)
            print("     wrong rbp version or already modified by another tool",
                  file=sys.stderr)
            return 2
        struct.pack_into("<I", data, off, new)
        applied += 1

    print(f"[+] patches: {applied} applied, {already} already present, "
          f"{len(PATCHES)} total")
    if args.check:
        print("[i] --check only, no output written")
        return 0

    with open(args.output, "wb") as fh:
        fh.write(data)
    print(f"[+] wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())