push ebx
add esp, 0xFFFFFFB0
mov ebx, eax
push 0x3F800000
push 0x3F800000
push 0x3F800000
push 0
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x10]
call GfxVertex
push esp
push 0
push 0x3F800000
push 0
push 0
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x28]
call GfxVertex
lea eax, dword ptr ss:[esp+0x18]
push eax
push 0x3F800000
push 0
push 0x3F800000
push 0x3F800000
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x40]
call GfxVertex
lea eax, dword ptr ss:[esp+0x30]
push eax
push 0
push 0
push 0
push 0x3F800000
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x58]
call GfxVertex
lea edx, dword ptr ss:[esp+0x48]
mov eax, ebx
pop ecx
call GfxDrawQuad
add esp, 0x50
pop ebx
ret
