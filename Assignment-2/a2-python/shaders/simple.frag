#version 330 core

uniform sampler2D imageTexture;

uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 light2Pos;
uniform vec3 light2Color;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

out vec4 outColor;

void main()
{
    vec3 texColour = texture(imageTexture, TexCoord).rgb;
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    int specAlpha = 32;
    float specCoefficient = 0.4;

    /////////// SUN LIGHT ///////////
    vec3 lightDir = normalize(lightPos - FragPos);

    // Ambient light I_a
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * lightColor;

    // Diffuse light I_d
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // Specular light I_s
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), specAlpha);
    vec3 specular = specCoefficient * spec * lightColor;

    /////////// SECOND LIGHT ///////////
    vec3 light2Dir = normalize(light2Pos - FragPos);
    float diff2 = max(dot(norm, light2Dir), 0.0);
    vec3 diffuse2 = diff2 * light2Color;
    vec3 reflectDir2 = reflect(-light2Dir, norm);
    float spec2 = pow(max(dot(viewDir, reflectDir2), 0.0), specAlpha);
    vec3 specular2 = specCoefficient * spec2 * light2Color;

    // Phong model I = I_a + I_d + I_s
    vec3 lighting = ambient + diffuse + specular + diffuse2 + specular2;
    lighting = min(lighting, vec3(1.0)); //prevent lighting values > 1

    vec3 result = texColour * lighting;
    outColor = vec4(result, 1.0);
}
