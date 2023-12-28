mov dword ptr ds:[keypress_buffer_eax], eax
mov eax, dword ptr ds:[ecx]
mov dword ptr ds:[keypress_buffer_key], eax
inc dword ptr ds:[keypress_buffer_inc]
mov eax, dword ptr ds:[keypress_buffer_eax]
execute_stolen:
    push ebp
    mov ebp, esp
    add esp, 0xFFFFFFEC
jmp 0x00589BD6