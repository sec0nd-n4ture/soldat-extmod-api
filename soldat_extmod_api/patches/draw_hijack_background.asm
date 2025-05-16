mov dword ptr ds:[ic_ptr_eax_save], eax
mov dword ptr ds:[ic_ptr_ebx_save], ebx
mov dword ptr ds:[ic_ptr_ecx_save], ecx
mov dword ptr ds:[ic_ptr_edx_save], edx
mov dword ptr ds:[ic_ptr_ebp_save], ebp
mov dword ptr ds:[ic_ptr_esp_save], esp
mov dword ptr ds:[ic_ptr_esi_save], esi
mov dword ptr ds:[ic_ptr_edi_save], edi

mov eax, background_fbo
mov eax, dword ptr ds:[eax]
cmp eax, 0
je execute_stolen
call GfxTarget

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
    mov byte ptr ss:[ebp-1], al
    jmp 0x005CC676
