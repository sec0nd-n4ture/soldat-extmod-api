mov dword ptr ds:[keypress_buffer_eax], eax
mov eax, dword ptr ds:[ecx]
mov dword ptr ds:[keypress_buffer_key], eax
inc dword ptr ds:[keypress_buffer_inc]
mov eax, dword ptr ds:[keypress_buffer_eax]
execute_stolen:
    push ebp
    mov ebp, esp
    push 0
    push 0
jmp FormKeyPressContinue