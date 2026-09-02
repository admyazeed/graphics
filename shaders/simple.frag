#version 330 core

uniform sampler2D imageTexture;

uniform vec3 viewPos;
uniform vec3 sunLightPos;
uniform vec3 sunLightColor;
uniform vec3 siriusPos;
uniform vec3 siriusColor;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

out vec4 outColor;

void main()
{
    vec3 texColour = texture(imageTexture, TexCoord).rgb;
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    int specAlpha = 64;
    float specCoefficient = 0.8;

    /////////// SUN LIGHT ///////////
    vec3 lightDir = normalize(sunLightPos - FragPos);

    // Ambient light I_a
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * sunLightColor;

    // Diffuse light I_d
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * sunLightColor;

    // Specular light I_s
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), specAlpha);
    vec3 specular = specCoefficient * spec * sunLightColor;

    /////////// SECOND LIGHT ///////////
    vec3 light2Dir = normalize(siriusPos - FragPos);
    float diff2 = max(dot(norm, light2Dir), 0.0);
    vec3 diffuse2 = diff2 * siriusColor;
    vec3 reflectDir2 = reflect(-light2Dir, norm);
    float spec2 = pow(max(dot(viewDir, reflectDir2), 0.0), specAlpha);
    vec3 specular2 = specCoefficient * spec2 * siriusColor;

    // Phong model I = I_a + I_d + I_s
    vec3 lighting = ambient + diffuse + specular + diffuse2 + specular2;
    lighting = min(lighting, vec3(1.0)); //prevent lighting values > 1

    vec3 result = texColour * lighting;
    outColor = vec4(result, 1.0);
}
