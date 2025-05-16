mov dword ptr ds:[ic_ptr_eax_save], eax
mov dword ptr ds:[ic_ptr_ebx_save], ebx
mov dword ptr ds:[ic_ptr_ecx_save], ecx
mov dword ptr ds:[ic_ptr_edx_save], edx
mov dword ptr ds:[ic_ptr_ebp_save], ebp
mov dword ptr ds:[ic_ptr_esp_save], esp
mov dword ptr ds:[ic_ptr_esi_save], esi
mov dword ptr ds:[ic_ptr_edi_save], edi

mov esi, dword ptr ds:[ptr_framebuffer_count]
cmp esi, 0
jz execute_stolen
mov ebx, ptr_framebuffer_array
fbo_iter_next:
    lea eax, dword ptr ds:[ebx+esi*4-4]
    call GfxDeleteTexture
    dec esi
    jnz fbo_iter_next

xor eax, eax
mov dword ptr ds:[ptr_framebuffer_count], eax

execute_stolen:
    mov eax, dword ptr ds:[ic_ptr_eax_save]
    mov ebx, dword ptr ds:[ic_ptr_ebx_save]
    mov ecx, dword ptr ds:[ic_ptr_ecx_save]
    mov edx, dword ptr ds:[ic_ptr_edx_save]
    mov ebp, dword ptr ds:[ic_ptr_ebp_save]
    mov esp, dword ptr ds:[ic_ptr_esp_save]
    mov esi, dword ptr ds:[ic_ptr_esi_save]
    mov edi, dword ptr ds:[ic_ptr_edi_save]
    push ebx
    push esi
    push edi
    push ecx
    mov edi, 0x005E9A6C
    jmp DC_continue
