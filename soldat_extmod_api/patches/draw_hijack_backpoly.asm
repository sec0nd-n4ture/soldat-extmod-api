mov dword ptr ds:[ic_ptr_eax_save], eax
mov dword ptr ds:[ic_ptr_ebx_save], ebx
mov dword ptr ds:[ic_ptr_ecx_save], ecx
mov dword ptr ds:[ic_ptr_edx_save], edx
mov dword ptr ds:[ic_ptr_ebp_save], ebp
mov dword ptr ds:[ic_ptr_esp_save], esp
mov dword ptr ds:[ic_ptr_esi_save], esi
mov dword ptr ds:[ic_ptr_edi_save], edi

cmp dword ptr ds:[draw_polygon_wireframe_flag], 0
je no_wireframe
mov eax, backpoly_wireframe_fbo
mov eax, dword ptr ds:[eax]
cmp eax, 0
je no_wireframe
call GfxTarget
xor eax, eax
call GfxBindTexture
cmp dword ptr ds:[wireframe_mode], 0
jne fill_mode
push 0x1B01
push 0x408
mov eax, dword ptr ds:[glPolygonMode]
call eax
fill_mode:
push 0
xor ecx, ecx
xor edx, edx
xor eax, eax
call RGBAOverload2
call GfxClear
mov eax, dword ptr ds:[wireframe_vbo]
cmp dword ptr ds:[wireframe_vbo], 0
je default_vbo
mov ecx, dword ptr ss:[ebp-0x8]
mov edx, dword ptr ds:[ecx+0x9C]
mov ecx, dword ptr ds:[ecx+0xA0]
jmp draw_wireframe_back
default_vbo:
mov eax, dword ptr ss:[ebp-0x8]
mov ecx, dword ptr ds:[eax+0xA0]
mov edx, dword ptr ds:[eax+0x9C]
mov eax, dword ptr ds:[eax+0x10]
draw_wireframe_back:
call GfxDraw
cmp dword ptr ds:[wireframe_mode], 0
jne no_wireframe
push 0x1B02
push 0x408
mov eax, dword ptr ds:[glPolygonMode]
call eax
no_wireframe:
mov eax, backpoly_fbo
mov eax, dword ptr ds:[eax]
cmp eax, 0
je execute_stolen
call GfxTarget
push 0
xor ecx, ecx
xor edx, edx
xor eax, eax
call RGBAOverload2
call GfxClear
execute_stolen:
    mov eax, dword ptr ds:[ic_ptr_eax_save]
    mov ebx, dword ptr ds:[ic_ptr_ebx_save]
    mov ecx, dword ptr ds:[ic_ptr_ecx_save]
    mov edx, dword ptr ds:[ic_ptr_edx_save]
    mov ebp, dword ptr ds:[ic_ptr_ebp_save]
    mov esp, dword ptr ds:[ic_ptr_esp_save]
    mov esi, dword ptr ds:[ic_ptr_esi_save]
    mov edi, dword ptr ds:[ic_ptr_edi_save]
    xor eax, eax
    cmp dword ptr ds:[disable_poly_texture_flag], 1
    je  0x005CCA19
    mov eax, dword ptr ss:[ebp-0x08]
    mov eax, dword ptr ds:[eax+0x18]
    jmp 0x005CCA19
