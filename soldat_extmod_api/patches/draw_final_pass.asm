mov dword ptr ds:[ic_ptr_eax_save], eax
mov dword ptr ds:[ic_ptr_ebx_save], ebx
mov dword ptr ds:[ic_ptr_ecx_save], ecx
mov dword ptr ds:[ic_ptr_edx_save], edx
mov dword ptr ds:[ic_ptr_ebp_save], ebp
mov dword ptr ds:[ic_ptr_esp_save], esp
mov dword ptr ds:[ic_ptr_esi_save], esi
mov dword ptr ds:[ic_ptr_edi_save], edi

mov ecx, dword ptr ds:[ptr_shader_count]
mov ebx, ptr_shader_array
iter_shaders:
    test ecx, ecx
    jz combine_framebuffers
    mov eax, 0x1A
    imul eax, ecx
    sub eax, 0x1A
    add eax, ebx
    dec ecx
    xor edx, edx
    mov dl, byte ptr ds:[eax]
    cmp dl, 0
    jz iter_shaders
    mov dl, byte ptr ds:[eax+1]
    cmp dl, 7
    je iter_shaders
    mov esi, dword ptr ds:[eax+2]
    mov edi, dword ptr ds:[eax+6]
    push ecx
    push ebx
    mov ecx, dword ptr ds:[eax+0x0a]
    lea ebx, dword ptr ds:[eax+0x0e]
    call ApplyShader
    pop ebx
    pop ecx
    jmp iter_shaders
combine_framebuffers:
    mov eax, dword ptr ds:[final_pass_fbo]
    call SwitchRenderTargetClearkeeptransparent
    call GfxBegin
    mov eax, dword ptr ds:[background_fbo]
    call DrawFullscreenQuad
    call GfxEnd
    call GfxBegin
    mov eax, dword ptr ds:[props_fbo0]
    call DrawFullscreenQuad
    call GfxEnd
    call GfxBegin
    mov eax, dword ptr ds:[players_fbo]
    call DrawFullscreenQuad
    call GfxEnd
    call GfxBegin
    mov eax, dword ptr ds:[props_fbo1]
    call DrawFullscreenQuad
    call GfxEnd
    call GfxBegin
    mov eax, dword ptr ds:[poly_fbo]
    call DrawFullscreenQuad
    call GfxEnd
    call GfxBegin
    mov eax, dword ptr ds:[props_fbo2]
    call DrawFullscreenQuad
    call GfxEnd
    call IterPostprocessShaders
    call GfxBegin
    mov eax, dword ptr ds:[interface_fbo]
    call DrawFullscreenQuad
    call GfxEnd
    xor eax, eax
    call SwitchRenderTargetClearkeeptransparent
    call GfxBegin
    mov eax, dword ptr ds:[final_pass_fbo]
    call DrawFullscreenQuad
    call GfxEnd


execute_stolen:
    mov eax, dword ptr ds:[ic_ptr_eax_save]
    mov ebx, dword ptr ds:[ic_ptr_ebx_save]
    mov ecx, dword ptr ds:[ic_ptr_ecx_save]
    mov edx, dword ptr ds:[ic_ptr_edx_save]
    mov ebp, dword ptr ds:[ic_ptr_ebp_save]
    mov esp, dword ptr ds:[ic_ptr_esp_save]
    mov esi, dword ptr ds:[ic_ptr_esi_save]
    mov edi, dword ptr ds:[ic_ptr_edi_save]
    mov eax, dword ptr ds:[0x005E3D5C]
    jmp 0x005CD021

SwitchRenderTargetCleartransparent:
    push eax
    push ecx
    push edx
    call GfxTarget
    mov eax, dword ptr ds:[screen_height]
    mov eax, dword ptr ds:[eax]
    push eax
    mov ecx, dword ptr ds:[screen_width]
    mov ecx, dword ptr ds:[ecx]
    xor edx, edx
    xor eax, eax
    call GfxViewport
    push 0
    xor ecx, ecx
    xor edx, edx
    xor eax, eax
    call RGBAOverload2
    call GfxClear
    pop edx
    pop ecx
    pop eax
    ret

SwitchRenderTargetClearkeeptransparent:
    push eax
    push ecx
    push edx
    call GfxTarget
    mov eax, dword ptr ds:[screen_height]
    mov eax, dword ptr ds:[eax]
    push eax
    mov ecx, dword ptr ds:[screen_width]
    mov ecx, dword ptr ds:[ecx]
    xor edx, edx
    xor eax, eax
    call GfxViewport
    mov dl, 0xFF
    xor eax, eax
    call RGBA
    call GfxClear
    pop edx
    pop ecx
    pop eax
    ret

IterPostprocessShaders:
    mov ecx, dword ptr ds:[ptr_shader_count]
    mov ebx, ptr_shader_array
    iter_post_proc_shaders:
        test ecx, ecx
        jz exit
        mov eax, 0x1A
        imul eax, ecx
        sub eax, 0x1A
        add eax, ebx
        dec ecx
        xor edx, edx
        mov dl, byte ptr ds:[eax]
        cmp dl, 0
        jz iter_post_proc_shaders
        mov dl, byte ptr ds:[eax+1]
        cmp dl, 7
        jne iter_post_proc_shaders
        mov esi, dword ptr ds:[eax+2]
        mov edi, dword ptr ds:[eax+6]
        push ecx
        push ebx
        mov ecx, dword ptr ds:[eax+0x0a]
        lea ebx, dword ptr ds:[eax+0x0e]
        call ApplyShader
        pop ebx
        pop ecx
        jmp iter_post_proc_shaders
    exit:
        ret

ApplyShader:
    push edx
    mov eax, esi
    call SwitchRenderTargetCleartransparent
    push ecx
    push edi
    mov eax, dword ptr ds:[pglUseProgram]
    mov eax, dword ptr ds:[eax]
    call eax
    pop ecx
    cmp ecx, 0xFFFFFFFF
    je no_time_update
    update_time_uniform:
        call UpdateTimeUniform
    no_time_update:
        mov ecx, dword ptr ds:[ebx]
        cmp ecx, 0xFFFFFFFF
        je no_velocity_update
    update_velocity:
        call UpdateVelocityUniform
    no_velocity_update:
        mov ecx, dword ptr ds:[ebx+8]
        cmp ecx, 0xFFFFFFFF
        je no_camera_pos_update
    camera_pos_update:
        call UpdateCameraPos
    no_camera_pos_update:
        call GfxBegin
        pop edx
        mov eax, dword ptr ds:[background_fbo+edx*4]
        push edx
        call DrawFullscreenQuadShader
        call GfxEnd
        pop edx
        mov eax, dword ptr ds:[background_fbo+edx*4]
        call SwitchRenderTargetCleartransparent
        mov eax, dword ptr ds:[ptr_default_shader_handle]
        push eax
        mov eax, dword ptr ds:[pglUseProgram]
        mov eax, dword ptr ds:[eax]
        call eax
        call GfxBegin
        mov eax, esi
        call DrawFullscreenQuad
        call GfxEnd
    ret

UpdateTimeUniform:
    add esp, 0xFFFFFFF8
    call GetTickCount
    mov dword ptr ss:[esp], eax
    xor eax, eax
    mov dword ptr ss:[esp+4], eax
    fild qword ptr ss:[esp]
    fdiv dword ptr ds:[thousand_constant]
    add esp, 0xFFFFFFFC
    fstp dword ptr ss:[esp]
    fwait 
    push ecx
    mov eax,dword ptr ds:[glUniform1f]
    call eax
    pop ecx
    pop edx
    ret

UpdateVelocityUniform:
    mov ebx, dword ptr ds:[ebx+4]
    push dword ptr ds:[ebx+4]
    push dword ptr ds:[ebx]
    push ecx
    mov eax, dword ptr ds:[glUniform2f]
    call eax
    ret

UpdateCameraPos:
    push dword ptr ds:[camera_world_pos_y]
    push dword ptr ds:[camera_world_pos_x]
    push ecx
    mov eax, dword ptr ds:[glUniform2f]
    call eax
    ret
