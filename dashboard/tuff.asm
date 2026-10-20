mov eax, 5       ; 
mov ebx, ecx     ; 
mov [ebx], eax   
dot_product:
    vxorps      zmm0, zmm0, zmm0    ; Clear primary accumulator vector
    vxorps      zmm1, zmm1, zmm1    ; Clear secondary accumulator loop unroll
    xor         rcx, rcx            ; Array index = 0

.loop_unrolled_64:
    cmp         rdx, 64
    jl          .loop_16            ; Less than 64 elements left? Drop to single vector loop.

    ; Unrolled by 4 to maximize CPU execution pipeline throughput
    vmovups     zmm2, [rdi + rcx*4]       ; Load 16 floats from A
    vmovups     zmm3, [rdi + rcx*4 + 64]  ; Load next 16 floats from A
    vfmadd231ps zmm0, zmm2, [rsi + rcx*4]       ; zmm0 += zmm2 * B[rcx]
    vfmadd231ps zmm1, zmm3, [rsi + rcx*4 + 64]  ; zmm1 += zmm3 * B[rcx+16]

    vmovups     zmm4, [rdi + rcx*4 + 128]
    vmovups     zmm5, [rdi + rcx*4 + 192]
    vfmadd231ps zmm0, zmm4, [rsi + rcx*4 + 128]
    vfmadd231ps zmm1, zmm5, [rsi + rcx*4 + 192]

    add         rcx, 64             ; Move ahead 64 elements
    sub         rdx, 64             ; Decrement loop counter
    jmp         .loop_unrolled_64

.loop_16:
    cmp         rdx, 16
    jl          .epilogue_mask      ; Leftovers < 16? Use masked vector operations.

    vmovups     zmm2, [rdi + rcx*4]
    vfmadd231ps zmm0, zmm2, [rsi + rcx*4]
    add         rcx, 16
    sub         rdx, 16
    jmp         .loop_16

.epilogue_mask:
    test        rdx, rdx
    jz          .horizontal_reduction ; No elements left, proceed to horizontal reduce.

    ; Handle dynamic odd boundaries (e.g. 7 elements remaining) using mask registers
    mov         rax, 1
    shl         rax, cl             ; Shift bit count (cl = lowest byte of rdx)
    dec         rax                 ; Formulate tail mask bit pattern (e.g., 00000111)
    kmovq       k1, rax             ; Load masking state to AVX k-register

    vmovups     zmm2 {k1}{z}, [rdi + rcx*4]   ; Masked load (zero remaining vector slots)
    vfmadd231ps zmm0 {k1}, zmm2, [rsi + rcx*4] ; Safely process tail elements without faults

.horizontal_reduction:
    vaddps      zmm0, zmm0, zmm1    ; Fold unrolled accumulator zmm1 into zmm0
    
    ; Extract and horizontally collapse 512-bit vector down into single scalar xmm0 float
    vextractf64x4 ymm2, zmm0, 1     ; Extract upper 256 bits
    vaddps      ymm0, ymm0, ymm2    ; Add upper 256 to lower 256 bits
    vextractf128 xmm2, ymm0, 1      ; Extract upper 128 bits
    vaddps      xmm0, xmm0, xmm2    ; Add upper 128 to lower 128 bits
    vshufps     xmm2, xmm0, xmm0, 0x4E ; Swap middle halves
    vaddps      xmm0, xmm0, xmm2
    vshufps     xmm2, xmm0, xmm0, 0x11 ; Swap adjacent float spaces
    vaddps      xmm0, xmm0, xmm2    ; xmm0[0] now contains absolute scalar sum
    ret
