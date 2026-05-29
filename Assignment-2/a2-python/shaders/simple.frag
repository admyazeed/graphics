#version 330 core

uniform sampler2D imageTexture;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 viewPos;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

out vec4 outColor;

void main()
{
    vec3 texColour = texture(imageTexture, TexCoord).rgb;
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);

    // Ambient light I_a
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * lightColor;

    // Diffuse light I_d
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // Specular light I_s
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    int specAlpha = 32;
    float specCoefficient = 0.4;
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), specAlpha);
    vec3 specular = specCoefficient * spec * lightColor;

    // Phong model I = I_a + I_d + I_s
    vec3 lighting = ambient + diffuse + specular;

    vec3 result = texColour * lighting;
    outColor = vec4(result, 1.0);
}
