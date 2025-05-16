push ebx
push esi
push edi
push ebp
add esp, 0xFFFFFFEC
mov dword ptr ss:[esp],edx
mov edi, eax
mov eax,dword ptr ds:[edi+8]
mov dword ptr ss:[esp+4],eax
mov esi,dword ptr ds:[edi+0xC]
mov ebx,dword ptr ss:[esp+4]
shl ebx,2
mov eax,dword ptr ss:[esp+4]
imul esi
mov ebp,eax
shl ebp,2
mov eax,ebp
call GetMem
mov dword ptr ss:[esp+8],eax
mov eax, dword ptr ds:[0x005E9A94]
push eax
push 0x8D40
mov eax, dword ptr ds:[0x005E47A0]
mov eax,dword ptr ds:[eax]
call eax
push 0
mov eax,dword ptr ds:[edi+4]
push eax
push 0xDE1
push 0x8CE0
push 0x8D40
mov eax, dword ptr ds:[0x005E4230]
mov eax,dword ptr ds:[eax]
call eax
mov eax,dword ptr ss:[esp+8]
push eax
push 0x1401
push 0x1908
push esi
mov eax,dword ptr ss:[esp+0x14]
push eax
push 0
push 0
mov eax,dword ptr ds:[0x005E723C]
call eax
mov eax,ebp
call GetMem
mov dword ptr ss:[esp+0xC],eax
mov ecx,ebp
mov edx,dword ptr ss:[esp+0xC]
mov eax,dword ptr ss:[esp+0x8]
call Move
mov ebp,dword ptr ss:[esp+0x8]
mov edi,esi
dec edi
test edi,edi
jl loop_continue
inc edi
mov dword ptr ss:[esp+0x10], 0
loop_continue:
    mov edx,ebp
    mov eax,esi
    dec eax
    sub eax,dword ptr ss:[esp+0x10]
    imul eax,ebx
    add eax,dword ptr ss:[esp+0xC]
    mov ecx,ebx
    call Move
    add ebp,ebx
    inc dword ptr ss:[esp+0x10]
    dec edi
    jne loop_continue
loop_exit:
    push ebx
    mov eax,dword ptr ss:[esp+0xC]
    push eax
    push 0x4
    push esi
    mov eax,dword ptr ss:[esp+0x14]
    push eax
    mov eax,dword ptr ss:[esp+0x14]
    call LStrToPChar
    push eax
    call Stbi_write_png
    add esp, 0x18
    mov eax,dword ptr ss:[esp+0xC]
    call FreeMem
    mov eax,dword ptr ss:[esp+0x8]
    call FreeMem
    add esp, 0x14
    pop ebp
    pop edi
    pop esi
    pop ebx
    ret