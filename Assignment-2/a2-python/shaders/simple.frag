#version 330 core

uniform sampler2D imageTexture;

in vec2 TexCoord;

out vec4 outColor;

void main()
{
    outColor = texture(imageTexture, TexCoord);
}
