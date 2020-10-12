reset:
    ; The very first thing to do when powering on is to put all sources
    ; of interrupts into a known state.
    sei             ; Disable interrupts
    ldx #$00
    stx $2000     ; Disable NMI and set VRAM increment to 32
    stx $2001     ; Disable rendering
    stx $4010       ; Disable DMC IRQ
    dex             ; Subtracting 1 from $00 gives $FF, which is a
    txs
    bit $2002
    bit $4015      ; Acknowledge DMC IRQ
    lda #$40
    ;sta P2
    lda #$0F
    sta $4015

vblank_wait1:
    bit $2002
    bpl vblank_wait1
    cld

    lda #$00
clear_zp:
    sta $00,x
    inx
    bne clear_zp

vblank_wait2:
    bit $2002  ; After the second vblank, we know the PPU has
    bpl vblank_wait2     ; fully stabilized.


; PPU stabilized
main:
    jmp main