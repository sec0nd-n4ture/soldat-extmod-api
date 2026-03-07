push eax
push ebx
push edx
mov ebx, eax
mov ebx, dword ptr ds:[ebx-4]
mov dword ptr ds:[map_vbosize_ptr], ebx
mov ebx, eax
cmp dword ptr ds:[map_vbo_ptr], 0
je copy_vbo_data
push 0x8000
push 0
push dword ptr ds:[map_vbo_ptr]
call VirtualFree
copy_vbo_data:
push 0x4
push 0x00003000
push dword ptr ds:[ebx-0xc]
push 0
call VirtualAlloc
test eax, eax
jz exit
mov dword ptr ds:[map_vbo_ptr], eax
push dword ptr ds:[ebx-0xc]
push ebx
push eax
call Memcpy
add esp, 0xC
exit:
pop edx
pop ebx
pop eax
call 0x00406870
jmp 0x005CAB5F