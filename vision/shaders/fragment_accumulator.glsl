#version 420 core

layout (r32ui) uniform uimageBuffer image_buffer;  

// DEBUG
out vec4 fragment_color;

void main(void){
    int loc = int((gl_FragCoord.y - .5) * 1024 + gl_FragCoord.x);
    imageAtomicAdd(image_buffer, loc, 1);

    // DEBUG
    fragment_color = vec4(1.0, 1.0, 1.0, 1);
}