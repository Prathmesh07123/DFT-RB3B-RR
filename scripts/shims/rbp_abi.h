/* -------- Ganpati Bappa Morya --------
 * rbp_abi.h -- Addresses and constants for the XDJ-RR rbp binary.
 *
 * XDJ-RR rbp: md5 05842e98fa66ace854e3d825de65ea29, 7,001,108 bytes, v1.08
 * XDJ-RX3 rbp: md5 4f2efcfc0c9e3f539289f863acfddcc6, 7,620,543 bytes, v1.20
 *
 * Format: "RR (RX3: 0xOLD)" = changed for XDJ-RR.
 *         "both"            = same on both devices.
 *         "TODO"            = not yet found on XDJ-RR.
 */
#ifndef RBPI4B_RBP_ABI_H
#define RBPI4B_RBP_ABI_H

/* ============================================================
 * SECTION 1 -- VERIFIED XDJ-RR ADDRESSES
 * ============================================================ */

/* ---- Singletons / Global pointers ---- */
#define UI_OBJ_MGR_GLOBAL        0x0187266cUL   /* RR (RX3: 0x02685f2c)  uiObjectManager */
#define UI_OBJ_MGR_HOLDER        0x01872e80UL   /* RR (RX3: 0x026867c0)  UiObjectManager::instance */
#define UIOBJ_HOLDER_GLOBAL      0x01872e80UL   /* RR (RX3: 0x026867c0) */
#define LEDMGR_HOLDER_GLOBAL     0x01872e80UL   /* RR (RX3: 0x026867c0) */
#define ME_SINGLETON             0x010d6500UL   /* RR (RX3: 0x011493c0)  MixerEngine::_singletonInstance */
#define PLAYENGINE_GLOBAL        0x010d68b0UL   /* RR (RX3: 0x011497d0)  PlayEngine::_singletonInstance */
#define ALOOP_PLAYENGINE_GLOBAL  0x010d68b0UL   /* RR (RX3: 0x011497d0) */
#define NM_SINGLETON             0x01875ee8UL   /* RR (RX3: 0x026873d8)  NetworkManager::_singletonInstance */
#define UIBROWSE_GLOBAL          0x01e2f67cUL   /* RR (RX3: 0x0326f8b8)  uiBrowse */
#define MIXER_ROUTE_PLAYER0      0x010d6cb8UL   /* RR (RX3: 0x01149f50)  MixerRouteMngr::m_stPlayerOutput[0] */
#define MIXER_ROUTE_PLAYER1      0x010d6cbcUL   /* RR (RX3: 0x01149f54)  MixerRouteMngr::m_stPlayerOutput[1] */
#define MIXER_ROUTE_INPUT0       0x010d6cf8UL   /* RR (RX3: 0x01149f08)  MixerRouteMngr::m_stMixerInput[0] */
#define MIXER_ROUTE_INPUT1       0x010d6cfcUL   /* RR (RX3: 0x01149f10)  MixerRouteMngr::m_stMixerInput[1] */

/* ---- MixerEngine: headphone cue (PFL) ---- */
#define ME_SET_CUE               0x00052f64UL   /* RR (RX3: 0x000575a0)  setInputChHeadphoneCue */
#define ME_GET_CUE               0x00052fd4UL   /* RR (RX3: 0x000575e8)  isInputChHeadphoneCue */
#define ME_SET_STEREO            0x00053060UL   /* RR (RX3: 0x0005768c)  setHeadphoneStereoType */
#define ME_SET_MASTER_CUE        0x00053040UL   /* RR (RX3: 0x0005766c)  setOutputChHeadphoneCue */
#define ME_GET_MASTER_CUE        0x00053050UL   /* RR (RX3: 0x0005767c)  isOutputChHeadphoneCue */

/* ---- Beat FX ---- */
#define ADDR_GET_BFX_TYPE        0x0004a7f0UL   /* RR (RX3: 0x0004d514) DjEngineIF::getBeatEffectType */

/* ---- Hot cue (engine side) ---- */
#define ADDR_ENGINE_CLEAR_HOTCUE 0x0005ac50UL   /* RR (RX3: 0x00048a48)  PlayEngine::clearHotCue */
#define ADDR_ENGINE_IS_REGHOTCUE 0x00046894UL   /* RR (RX3: 0x00048b00)  DjEngineIF::isRegisteredHotCue */
#define ADDR_HOTCUE_DELETE       0x00272924UL   /* RR (RX3: 0x002fb328)  Player::onHotCueDeleteEvent */

/* ---- Meter hook ---- */
#define ADDR_GETLEDVALUE         0x0024819cUL   /* RR (RX3: 0x0002d07a8) Mixer::MonoLvMeter::getLedValue */
#define RET_MASTER               0x0024831cUL   /* RR (RX3: 0x2d0940) */
#define RET_CH1                  0x00248404UL   /* RR (RX3: 0x2d0a44) */
#define RET_CH2                  0x00248520UL   /* RR (RX3: 0x2d0a8c) */
#define PROLOGUE_GETLED          0xe92d4070u    /* both */

/* ---- PlayEngine query methods ---- */
#define PE_ISPLAYING             0x000599d8UL   /* RR (RX3: 0x0005d880) */
#define PE_ISLOADED              0x000595e8UL   /* RR (RX3: 0x0005d3b0) */
#define PE_ISSYNCON              0x0005bbe4UL   /* RR (RX3: 0x0005ff28) */
#define PE_ISMASTERTEMPO         0x00059f60UL   /* RR (RX3: 0x0005dfa8) */
#define PE_ISVINYLMODE           0x0005a1e8UL   /* RR (RX3: 0x0005e260) */
#define PE_ISSLIPMODEON          0x0005b9f4UL   /* RR (RX3: 0x0005fc60) */
#define PE_ISLOOPING             0x0005a9f8UL   /* RR (RX3: 0x0005eadc) */
#define PE_ISAUTOBEATLOOP        0x0005ae04UL   /* RR (RX3: 0x0005ef74) */

/* ---- Other PlayEngine methods (verified) ---- */
#define PE_ISCANRELOOP           0x0005a9ccUL   /* RR (RX3: 0x0005eab0) isPossibleToReLoop */
#define PE_ISLOOPINADJ           0x0005ae90UL   /* RR (RX3: 0x0005f000) isLoopInAdjustMode */
#define PE_ISLOOPOUTADJ          0x0005aebcUL   /* RR (RX3: 0x0005f02c) isLoopOutAdjustMode */

/* ---- Wave / Grid ---- */
#define WAVE_SCALE_GLOBAL        0x016be488UL   /* RR (RX3: 0x0216bac8) */
#define WAVE_SCALE_GET           0x000fa618UL   /* RR function getPlayModeWaveScale */
#define WAVE_SCALE_SET           0x000fa628UL   /* RR function setPlayModeWaveScale */
#define GRID_ADJUST_FLG_GLOBAL   0x01e700ecUL   /* RR (RX3: 0x03254a9c) uiGridAdjust (BSS) */
#define GRID_ADJUST_GET          0x00136b60UL   /* RR function */
#define GRID_ADJUST_SET          0x00136b4cUL   /* RR function */
#define BROWSE_MODE_UTILITY      7              /* both */
#define BROWSE_MODE_PLAY         1              /* both */
#define WAVE_SCALE_MIN           0              /* both */
#define WAVE_SCALE_MAX           4              /* both */

/* ---- Pad mode (XDJ-RR specific) ---- */
#define UI_PADMODE_HOLDER_GLOBAL 0x0187266cUL   /* RR (RX3: 0x02685f2c) same as UI_OBJ_MGR_GLOBAL */
#define PADMODE_STATWATCHER_OFF  0x38           /* both */
#define PADMODE_DECK1_OFF        0x0c           /* both */
#define PADMODE_DECK2_OFF        0x10           /* both */
#define PADMODE_BYTE_OFF         0x281          /* both */

/* XDJ-RR has split the pad mode getter into several functions.
 * XDJ-RX3 had one UiGetPadMode @ 0x000fd3cc that returned
 * 0=HOT CUE / 1=AUTO BEAT LOOP / 2=SLIP BEAT LOOP / 3=BEAT JUMP.
 *
 * On XDJ-RR the closest equivalents are:
 */
#define UI_GET_PLAY_MODE         0x000df6e0UL   /* RR (RX3: 0x000fd3cc) UiGetPlayMode - reads play mode */
#define UI_GET_PADMODE_SLIPFLG   0x000df618UL   /* RR PadModeSlipLoopFlg */
#define UI_GET_PADMODE_SLIP_IN   0x000df648UL   /* RR PadModeSlipLoopINtime */
#define UI_GET_PADMODE_SLIP_OUT  0x000df680UL   /* RR PadModeSlipLoopOUTtime */

/* Use UI_GET_PLAY_MODE as the primary pad mode reader on XDJ-RR */
#define UI_GET_PADMODE           UI_GET_PLAY_MODE

/* ---- Pro DJ Link connect ---- */
#define NM_FN_CONNECT            0x00306facUL   /* RR (RX3: 0x0038f830) connectLink */
#define NM_FN_DISCONNECT         0x00306eccUL   /* RR alternative */
#define NM_FN_CONNECT_STOP       0x00306140UL   /* RR alternative */
#define NM_OFF_IP                0x24           /* both */
#define NM_OFF_CONNECT_FLG       0xc4           /* both */

/* ============================================================
 * SECTION 2 -- UI BROWSE STRUCTURE OFFSETS
 *   (C++ class layout, identical on XDJ-RX3 and XDJ-RR)
 * ============================================================ */

#define UIBROWSE_OFF_MODE        0x00           /* both */
#define UIBROWSE_OFF_DEVICE      0x04           /* both */
#define UIBROWSE_OFF_ACTIVE_LIST 0x14           /* both */
#define UIBROWSE_OFF_CURSOR      0x6c           /* both */
#define UIBROWSE_OFF_ITEMNUM     0x3b8          /* both */
#define UIBROWSE_OFF_INITIAL     0x3bc          /* both */
#define UIBROWSE_LIST_STRIDE     0x1ce4         /* both */
#define UIBROWSE_OFF_CALIB_A     0xac           /* both */
#define UIBROWSE_OFF_CALIB_B     0xb8           /* both */
#define UIBROWSE_OFF_PLAY_SUBGATE 0x18          /* both */

/* ============================================================
 * SECTION 3 -- UNIVERSAL CONSTANTS (same on both)
 * ============================================================ */

/* ---- Op codes ---- */
#define OP_PRESS      0
#define OP_REPEAT     1
#define OP_RELEASE    2
#define OP_ROTATE     4
#define OP_VALUE      5
#define CH_GLOBAL     1

/* ---- Keycodes ---- */
#define K_SELECTOR   0x420c
#define K_BROWSE     0x0202
#define K_SOURCE     0x0201
#define K_USB1       0x0209
#define K_LINK       0x0207
#define K_REKORDBOX  0x0208
#define K_TAGLIST    0x0203
#define K_MENU       0x0206
#define K_INFO       0x020b
#define K_PLAYLIST   0x0204
#define K_SEARCH     0x0205
#define K_SHORTCUT   0x0210
#define K_TRACKFILTER 0x420f
#define K_USBSTOP    0x8002
#define K_BACK       0x420d
#define K_LOAD       0x4311
#define K_PLAY       0x4101
#define K_CUE        0x4102
#define K_SYNC       0x4112
#define K_VINYL      0x4104
#define K_JOG_TOUCH  0x4306
#define K_JOG_ROT    0x4305
#define K_TEMPO_RANGE 0x4107
#define K_MT         0x4108
#define K_TEMPO_SLIDER 0x4109
#define K_QUANTIZE   0x410b
#define K_ALOOP      0x4114
#define K_HOTCUE     0x4113
#define K_SLIPLOOP   0x4115
#define K_BEATJUMP   0x4116
#define K_TRFWD      0x4214
#define K_TRREV      0x4215
#define K_SRFWD      0x411f
#define K_SRREV      0x4120
#define K_PAD1       0x4117
#define K_LOOPIN     0x410c
#define K_LOOPOUT    0x410d
#define K_RELOOP     0x410e
#define K_REV        0x410f
#define K_SLIP       0x4110
#define K_MASTER     0x4111
#define K_MASTERCUE  0x4407
#define K_TRIM       0x5019
#define K_EQH        0x501a
#define K_EQM        0x501b
#define K_EQL        0x501c
#define K_FADER      0x501e
#define K_XFADER     0x6017
#define K_HPMIX      0x4405
#define K_HPLEVEL    0x4406
#define K_MASTERLVL  0x4403
#define K_COLOR      0x509d
#define K_FILTER     0x50a6
#define K_DUBECHO    0x50a2
#define K_SWEEP      0x50a3
#define K_NOISE      0x50a4
#define K_SPACE      0x50a5
#define K_CRUSH      0x50a1
#define K_BFXTYPE    0x448b
#define K_BFXCH      0x448c
#define BFX_CH_MASTER 5
#define K_BFX        0x448d
#define K_TIME       0x448e
#define K_DEPTH      0x448f
#define K_BEATPREV   0x4490
#define K_BEATNEXT   0x4491
#define K_TAP        0x4492
#define K_EFFECTQUANT 0x0493
#define K_MIC        0x0814

/* ---- Object structure offsets ---- */
#define KEY_MANAGER_OFF          100
#define SENDKEY_VTABLE_WORD      2
#define UIOBJMGR_OFF_MGRNUM      0xcc
#define UIOBJMGR_OFF_MGRARR      0xc4
#define USB_MGR_OFF_CHANNEL      0x84
#define USB_MGR_OFF_MEDIA        0x88
#define USB_MGR_MEDIA_READY      2
#define UIOBJ_PLAYERS_OFF        64
#define UIOBJ_NPLAYERS_OFF       72
#define PLAYERINNARDS_CHAN_OFF   0x26
#define PLAYERINNARDS_ENGINE_OFF 0x30
#define PLAYERINNARDS_PADCMD_OFF 0x38
#define PLAYERINNARDS_MODE_OFF   0x74

/* ---- BeatEffectManager / BeatEffect offsets ---- */
#define BEM_IN_MIXER             0x58
#define BEM_OFF_SELECT_CH        0x00
#define BEM_OFF_EFFECT           0x08
#define BEM_OFF_TYPE             0x50
#define BE_OFF_DEPTH             0x20
#define BE_OFF_TIME              0x24
#define BE_OFF_ON                0x3c
#define BE_OFF_BEAT              0x44
#define BE_OFF_BEAT_MAX          0x48
#define BE_OFF_BEAT_MIN          0x4c
#define BFX_TYPE_OFF             0
#define BFX_DEPTH_FULL           1023
#define BFX_TYPE_POSITIONS       14

/* ---- LED table ---- */
#define LEDMGR_OFF_LEDSTAT       104
#define LEDSTAT_OFF              0x30
#define LED_ENTRY_SIZE           0x2c
#define LED_DUMP_MAX             256
#define LED_ENTRY_OFF_STATE      16
#define LED_ENTRY_OFF_PERIOD     28
#define LED_ENTRY_OFF_UNASSIGNED 20

/* ---- Mixer level table ---- */
#define MIXER_OFF                80
#define MIXER_LVLOFF             0xb8
#define RBP_METER_SEGMENTS       11

/* ---- LED stat IDs ---- */
#define LEDSTAT_PLAY             49
#define LEDSTAT_SYNC             4
#define LEDSTAT_VINYL            3
#define LEDSTAT_MT               6
#define LEDSTAT_SLIP             11

/* ---- Beat FX type-to-position map ---- */
static const signed char bfx_type_to_pos[15] = {
     -1, 5, 9, 10, 6, 1, 0, 3, 12, 7, 8, 13, 11, 2, 4
};

/* ---- AutoBeatLoop ---- */
#define ALOOP_POSITIONS          8
#define ADDR_EXEC_AUTOBEATLOOP   0x00278998UL   /* RR PlayerInnards::onKey_AutoBeatLoop (was XDJ-RX3 0x300c64) */
#define ADDR_GET_AUTOBEAT_BEATS  0x0027908cUL   /* RR PlayerInnards::getAutoBeatLoopBeats */
#define ADDR_SET_AUTOBEATLOOP    0x0005ad4cUL   /* RR PlayEngine::setAutoBeatLoop */
#define ADDR_START_AUTOBEATLOOP  0x000a3824UL   /* RR Loop::startAutoBeatLoop */

/* ---- Binary name ---- */
#define RBP_BIN_NAME             "rbp"

#endif /* RBPI4B_RBP_ABI_H */