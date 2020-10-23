; atari 2600 mapped registers
.define vsync $00
.define vblank $01
.define wsync $02
.define rsync $03
.define nusiz0 $04
.define nusiz1 $05
.define colup0 $06
.define colup1 $07
.define colupf $08                                                                                                     
.define colubk $09 
.define ctrlpf $0a
.define refp0 $0b
.define refp1 $0c
.define pf0 $0d
.define pf1 $0e
.define pf2 $0f
.define resp0 $10
.define resp1 $11
.define grp0 $1b
.define grp1 $1c
.define enam0 $1d
.define enam1 $1e
.define enabl $1f

start:
    lda #0
    sta vblank

    lda #2
    sta vsync

    sta wsync
    sta wsync
    sta wsync

    lda #0
    sta vsync

    ldx #37
scanlinewait:
    sta wsync
    dex
    bne scanlinewait

    ldx #0
scanlines:
    inx
    stx colubk
    sta wsync
    cpx #192
    bne scanlines

 
    lda #%01000010
    sta vblank

    ldx #37
overscan:
    sta wsync
    dex
    bne overscan

    jmp start

data:
    .byte $0, $88, $c8, $a8, $98, $88, $88, $0 ; N
    .byte $0, $f8, $20, $20, $20, $20, $f8, $0 ; I
    .byte $0, $f8, $80, $80, $80, $80, $f8, $0 ; C
    .byte $0, $f8, $80, $f8, $80, $80, $f8, $0 ; E
.org $ffa
.word start
.word start
.word start