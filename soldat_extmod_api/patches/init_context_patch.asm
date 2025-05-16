mov dword ptr ds:[ic_ptr_eax_save], eax
mov dword ptr ds:[ic_ptr_ebx_save], ebx
mov dword ptr ds:[ic_ptr_ecx_save], ecx
mov dword ptr ds:[ic_ptr_edx_save], edx
mov dword ptr ds:[ic_ptr_ebp_save], ebp
mov dword ptr ds:[ic_ptr_esp_save], esp
mov dword ptr ds:[ic_ptr_esi_save], esi
mov dword ptr ds:[ic_ptr_edi_save], edi

call CreateFrameBuffer
mov dword ptr ds:[background_fbo], eax
call CreateFrameBuffer
mov dword ptr ds:[props_fbo0], eax
call CreateFrameBuffer
mov dword ptr ds:[players_fbo], eax
call CreateFrameBuffer
mov dword ptr ds:[props_fbo1], eax
call CreateFrameBuffer
mov dword ptr ds:[poly_fbo], eax
call CreateFrameBuffer
mov dword ptr ds:[props_fbo2], eax
call CreateFrameBuffer
mov dword ptr ds:[interface_fbo], eax
call CreateFrameBuffer
mov dword ptr ds:[final_pass_fbo], eax
mov dword ptr ds:[ptr_framebuffer_count], 8
execute_stolen:
    mov eax, dword ptr ds:[ic_ptr_eax_save]
    mov ebx, dword ptr ds:[ic_ptr_ebx_save]
    mov ecx, dword ptr ds:[ic_ptr_ecx_save]
    mov edx, dword ptr ds:[ic_ptr_edx_save]
    mov ebp, dword ptr ds:[ic_ptr_ebp_save]
    mov esp, dword ptr ds:[ic_ptr_esp_save]
    mov esi, dword ptr ds:[ic_ptr_esi_save]
    mov edi, dword ptr ds:[ic_ptr_edi_save]
    cmp byte ptr ss:[ebp-0x02], 0x00
    jz IC_branch_1
    jmp IC_continue

CreateFrameBuffer:
    mov eax, dword ptr ds:[screen_width]
    mov eax, dword ptr ds:[eax]
    mov edx, dword ptr ds:[screen_height]
    mov edx, dword ptr ds:[edx]
    mov ecx, 4
    call GfxCreateRenderTarget
    ret