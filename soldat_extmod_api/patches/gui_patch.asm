mov al, byte ptr ds:[mem_shrd_redir_flag]
cmp al, 0x1
jne exit_norestore
jmp check_moreflags
exit_restore:
    mov ebx, dword ptr ds:[ptr_ebx_save]
    mov edx, dword ptr ds:[ptr_edx_save]
    mov ebp, dword ptr ds:[ptr_ebp_save]
    mov esp, dword ptr ds:[ptr_esp_save]
    mov esi, dword ptr ds:[ptr_esi_save]
    mov edi, dword ptr ds:[ptr_edi_save]
exit_norestore:
    push ebp
    mov ebp, esp
    mov ecx, ifacebyte
    xor eax, eax
    jmp RIhookContinue
create_texture:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    push dword ptr ds:[ptr_image]
    mov ecx, dword ptr ds:[ptr_imagecompr]
    mov edx, dword ptr ds:[ptr_imageheight]
    mov eax, dword ptr ds:[ptr_imagewidth]
    call GfxCreateTexture
    mov dword ptr ds:[ptr_ret_save], eax
    mov byte ptr ds:[flag_texture_func], 0x0
    jmp exit_restore
create_shader:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov eax, dword ptr ds:[ptr_shadertype]
    mov edx, dword ptr ds:[ptr_shadersource]
    call CreateShader
    mov dword ptr ds:[ptr_ret_save], eax
    mov byte ptr ds:[flag_shadercreate_func], 0x0
    jmp exit_restore
create_program:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov eax, dword ptr ds:[pglCreateProgram]
    mov eax, dword ptr ds:[eax]
    call eax
    mov dword ptr ds:[ptr_ret_save], eax
    mov byte ptr ds:[flag_progcreate_func], 0x0
    jmp exit_restore
attach_shader:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov ebx, dword ptr ds:[ptr_shaderhandle]
    push ebx
    mov ebx, dword ptr ds:[ptr_proghandle]
    push ebx
    mov eax, dword ptr ds:[pglAttachShader]
    mov eax, dword ptr ds:[eax]
    call eax
    mov byte ptr ds:[flag_attachshader_func], 0x0
    jmp exit_restore
link_program:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov ebx, dword ptr ds:[ptr_proghandle]
    push ebx
    mov eax, dword ptr ds:[pglLinkProgram]
    mov eax, dword ptr ds:[eax]
    call eax
    mov byte ptr ds:[flag_linkprog_func], 0x0
    jmp exit_restore
create_frame_buffer:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov eax, dword ptr ds:[screen_width]
    mov eax, dword ptr ds:[eax]
    mov edx, dword ptr ds:[screen_height]
    mov edx, dword ptr ds:[edx]
    mov ecx, 4
    call GfxCreateRenderTarget
    mov dword ptr ds:[ptr_ret_save], eax
    mov byte ptr ds:[flag_fbocreate_func], 0x0
    jmp exit_restore
get_uniform_location:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov ebx, dword ptr ds:[ptr_proghandle]
    push ebx
    mov eax, dword ptr ds:[pglUseProgram]
    mov eax, dword ptr ds:[eax]
    call eax
    mov eax, dword ptr ds:[ptr_uniformname]
    push eax
    push ebx
    mov eax, dword ptr ds:[pglGetUniformLocation]
    mov eax, dword ptr ds:[eax]
    call eax
    mov dword ptr ds:[ptr_ret_save], eax
    mov eax, dword ptr ds:[ptr_default_shader_handle]
    push eax
    mov eax, dword ptr ds:[pglUseProgram]
    mov eax, dword ptr ds:[eax]
    call eax
    mov byte ptr ds:[flag_getuniformloc_func], 0x0
    jmp exit_restore
check_moreflags:
    mov al, byte ptr ds:[flag_texture_func]
    cmp al, 0x1
    je create_texture
    mov al, byte ptr ds:[flag_shadercreate_func]
    cmp al, 0x1
    je create_shader
    mov al, byte ptr ds:[flag_progcreate_func]
    cmp al, 0x1
    je create_program
    mov al, byte ptr ds:[flag_attachshader_func]
    cmp al, 0x1
    je attach_shader
    mov al, byte ptr ds:[flag_linkprog_func]
    cmp al, 0x1
    je link_program
    mov al, byte ptr ds:[flag_fbocreate_func]
    cmp al, 0x1
    je create_frame_buffer
    mov al, byte ptr ds:[flag_getuniformloc_func]
    cmp al, 0x1
    je get_uniform_location
    mov al, byte ptr ds:[flag_draw_loop]
    cmp al, 0x1
    jne exit_norestore

    

    
gfx_draw_loop:
    mov dword ptr ds:[ptr_ebx_save], ebx
    mov dword ptr ds:[ptr_edx_save], edx
    mov dword ptr ds:[ptr_ebp_save], ebp
    mov dword ptr ds:[ptr_esp_save], esp
    mov dword ptr ds:[ptr_esi_save], esi
    mov dword ptr ds:[ptr_edi_save], edi
    mov ebx, dword ptr ds:[ptr_sprite_head]
    cmp ebx, 0x0
    je text_draw_loop
check_sprite_active:
    cmp byte ptr ds:[ebx+0x24], 0x1
    je check_sprite_type
sprite_iter_continue:
    mov ebx, dword ptr ds:[ebx+0x26]
    cmp ebx, 0x0
    je text_draw_loop
    jmp check_sprite_active
check_sprite_type:
    cmp byte ptr ds:[ebx+0x25], 0x1
    je sprite_draw_world
sprite_draw_screen:
    cmp byte ptr ds:[ebx+0x2e], 0x0
    je load_pos
    mov edi, dword ptr ds:[ebx+0x4]
    mov edi, dword ptr ds:[edi]
    push edi
    mov edi, dword ptr ds:[ebx+0x8]
    mov edi, dword ptr ds:[edi]
    push edi
    jmp load_scale
load_pos:
    push dword ptr ds:[ebx+0x4]
    push dword ptr ds:[ebx+0x8]
load_scale:
    push dword ptr ds:[ebx+0xC]
    push dword ptr ds:[ebx+0x10]
load_rot:
    push dword ptr ds:[ebx+0x14]
    push dword ptr ds:[ebx+0x18]
    push dword ptr ds:[ebx+0x1C]
    mov edx, dword ptr ds:[ebx+0x20]
    mov eax, dword ptr ds:[ebx]
    call GfxDrawSprite
    jmp sprite_iter_continue

sprite_draw_world:
    mov eax, fp_buffer
    add eax, 0x10
    mov esi, [ebx]
    add esi, 0x8
    mov esi, dword ptr ds:[esi]
    mov dword ptr ds:[eax], esi
    fild dword ptr ds:[eax]
    fstp dword ptr ds:[eax]
    push dword ptr ds:[eax]
    push dword ptr ds:[ebx+0xC]
    cmp byte ptr ds:[ebx+0x2e], 0x0
    je load_world_pos_x
    mov edi, dword ptr ds:[ebx+0x4]
    mov ecx, dword ptr ds:[edi]
    jmp load_world_pos_x_continue
load_world_pos_x:
    mov ecx, dword ptr ds:[ebx+0x4]
load_world_pos_x_continue:
    call WorldToScreenX
    mov eax, fp_buffer
    add eax, 0x10
    mov dword ptr ds:[eax], ecx
    fld dword ptr ds:[eax]
    fld dword ptr ds:[ebx+0x30]
    faddp st(1), st(0)
    fstp dword ptr ds:[eax]
    push dword ptr ds:[eax]
    mov eax, fp_buffer
    add eax, 0x10
    mov esi, [ebx]
    add esi, 0xC
    mov esi, dword ptr ds:[esi]
    mov dword ptr ds:[eax], esi
    fild dword ptr ds:[eax]
    fstp dword ptr ds:[eax]
    push dword ptr ds:[eax]
    push dword ptr ds:[ebx+0x10]
    cmp byte ptr ds:[ebx+0x2e], 0x0
    je load_world_pos_y
    mov edi, dword ptr ds:[ebx+0x8]
    mov ecx, dword ptr ds:[edi]
    jmp load_world_pos_y_continue
load_world_pos_y:
    mov ecx, dword ptr ds:[ebx+0x8]
load_world_pos_y_continue:
    call WorldToScreenY
    add esp, 0x8
    mov eax, fp_buffer
    add eax, 0x10
    mov dword ptr ds:[eax], ecx
    fld dword ptr ds:[eax]
    fld dword ptr ds:[ebx+0x34]
    faddp st(1), st(0)
    fstp dword ptr ds:[eax]
    push dword ptr ds:[eax]
    push dword ptr ds:[ebx+0xC]
    push dword ptr ds:[ebx+0x10]
    push dword ptr ds:[ebx+0x14]
    push dword ptr ds:[ebx+0x18]
    push dword ptr ds:[ebx+0x1C]
    mov edx, dword ptr ds:[ebx+0x20]
    mov eax, dword ptr ds:[ebx]
    call GfxDrawSprite
    jmp sprite_iter_continue

text_draw_loop:
    mov ebx, dword ptr ds:[ptr_text_count]
    inc ebx
    mov edi, ptr_text_array
check_text_active:
    cmp byte ptr ds:[edi], 0x1
    je check_text_type
text_iter_continue:
    dec ebx
    cmp ebx, 0x0
    je exit_restore
    add edi, 0x2C
    jmp check_text_active
check_text_type:
    mov eax, dword ptr ds:[edi+0x4]
    call GfxTextColor
    push dword ptr ds:[edi+0x1C]
    push dword ptr ds:[edi+0x20]
    mov eax, dword ptr ds:[edi+0x8]
    call GfxTextShadow
    push dword ptr ds:[edi+0x28]
    mov eax, dword ptr ds:[edi+0xC]
    call SetFontStyle
    push dword ptr ds:[edi+0x18]
    call GfxTextScale
    cmp byte ptr ds:[edi+1], 0x1
    je text_draw_world
text_draw_screen:
    push dword ptr ds:[edi+0x10]
    push dword ptr ds:[edi+0x14]
    mov eax, dword ptr ds:[edi+0x24]
    call GfxDrawText
    push 0x3f800000
    call GfxTextScale
    jmp text_iter_continue
text_draw_world:
    push dword ptr ds:[edi+0x18]
    push dword ptr ds:[edi+0x18]
    mov ecx, dword ptr ds:[edi+0x10]
    call WorldToScreenX
    push ecx
    push dword ptr ds:[edi+0x18]
    push dword ptr ds:[edi+0x18]
    mov ecx, dword ptr ds:[edi+0x14]
    call WorldToScreenY
    add esp, 0x8
    push ecx
    mov eax, dword ptr ds:[edi+0x24]
    call GfxDrawText
    push 0x3f800000
    call GfxTextScale
    jmp text_iter_continue

WorldToScreenX:
    mov eax, fp_buffer
    add eax, 0x4
    fld dword ptr ss:[esp+4]
    fld dword ptr ss:[esp+8]
    fmulp st(1), st(0)
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[camera_world_pos_x]
    add eax, 0x10
    mov dword ptr ds:[eax], ecx
    fld dword ptr ds:[eax]
    sub eax, 0x10
    fsubrp st(1), st(0)
    add eax, 0x4
    fstp dword ptr ds:[eax]
    sub eax, 0x4
    fld dword ptr ds:[eax]
    sub eax, 0x4
    fld dword ptr ds:[eax]
    fdivp st(0), st(1)
    add eax, 0xC
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[game_width_half]
    fld dword ptr ds:[eax]
    fsubp st(1), st(0)
    add eax, 0x4
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[eax]
    sub eax, 0x8
    fld dword ptr ds:[eax]
    faddp st(1), st(0)
    fstp dword ptr ds:[eax]
    mov ecx, dword ptr ds:[eax]
    ret

WorldToScreenY:
    mov eax, fp_buffer
    add eax, 0x4
    fld dword ptr ss:[esp+4]
    fld dword ptr ss:[esp+8]
    fmulp st(1), st(0)
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[camera_world_pos_y]
    add eax, 0x10
    mov dword ptr ds:[eax], ecx
    fld dword ptr ds:[eax]
    sub eax, 0x10
    fsubrp st(1), st(0)
    add eax, 0x4
    fstp dword ptr ds:[eax]
    sub eax, 0x4
    fld dword ptr ds:[eax]
    sub eax, 0x4
    fld dword ptr ds:[eax]
    fdivp st(0), st(1)
    add eax, 0xC
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[game_height_half]
    fld dword ptr ds:[eax]
    fsubp st(1), st(0)
    add eax, 0x4
    fstp dword ptr ds:[eax]
    fld dword ptr ds:[eax]
    sub eax, 0x8
    fld dword ptr ds:[eax]
    faddp st(1), st(0)
    fstp dword ptr ds:[eax]
    mov ecx, dword ptr ds:[eax]
    ret