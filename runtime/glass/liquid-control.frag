#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 surfaceSize;
    vec2 lightPosition;
    vec4 accentColor;
    float cornerRadius;
    float hoverAmount;
    float pressAmount;
    float selectedAmount;
    float restAmount;
    float bubbleAmount;
    float waveProgress;
    float waveAmplitude;
    vec2 waveOrigin;
};

// Translucent lighting over the compositor's live glass backdrop. No black
// shadow, scene capture, timer, or displacement of control contents/hit areas.
void main() {
    vec2 size = max(surfaceSize, vec2(1.0));
    vec2 p = qt_TexCoord0 * size - size * 0.5;
    // Keep the deformation inside the control, away from adjacent rows.
    vec2 squeeze = clamp(vec2(bubbleAmount * 0.012 * size.x,
                             bubbleAmount * 0.045 * size.y), vec2(-2.5), vec2(2.5));
    p *= size / max(size + squeeze, vec2(1.0));
    float waveFade = (1.0 - waveProgress) * waveAmplitude;
    float wobble = sin(atan(p.y, p.x) * 3.0 + waveProgress * 12.0) * waveFade * 0.9;
    float r = clamp(cornerRadius, 0.0, min(size.x, size.y) * 0.5);
    vec2 q = abs(p) - size * 0.5 + r + 2.5;
    float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r + wobble;
    float coverage = 1.0 - smoothstep(-0.7, 0.6, d);
    if (coverage < 0.001) { fragColor = vec4(0.0); return; }

    vec2 normal = normalize(max(q, vec2(0.0001))) * sign(p);
    if (q.x < 0.0 && q.y < 0.0)
        normal = q.x > q.y ? vec2(sign(p.x), 0.0) : vec2(0.0, sign(p.y));
    vec2 toPointer = lightPosition - qt_TexCoord0 * size;
    vec3 light = normalize(vec3(toPointer, max(size.y * 0.85, 18.0)));
    float facing = pow(max(dot(normal, light.xy) * 0.5 + 0.5, 0.0), 2.0);
    float depth = max(-d, 0.0);
    float rim = exp(-depth * 1.3);
    float shoulder = exp(-depth * 0.24);
    float spread = max(min(size.x * 0.45, 150.0), 32.0);
    float spot = exp(-dot(toPointer, toPointer) / (spread * spread));
    float topLight = 1.0 - qt_TexCoord0.y;
    float alpha = 0.025 * restAmount + 0.025 * selectedAmount;
    alpha += hoverAmount * (0.025 + spot * 0.075);
    alpha += shoulder * hoverAmount * facing * 0.07;
    alpha += rim * (0.12 * restAmount + 0.18 * selectedAmount
                    + hoverAmount * (0.18 + 0.34 * facing));
    alpha += pressAmount * (0.035 + shoulder * 0.12);
    alpha += shoulder * topLight * 0.025 * restAmount;
    float waveRadius = waveProgress * min(length(size) * 0.8, min(size.x, size.y) * 2.4);
    float waveBand = (length(qt_TexCoord0 * size - waveOrigin) - waveRadius) / 6.0;
    alpha += exp(-waveBand * waveBand) * waveFade * 0.22;
    vec3 hue = mix(vec3(1.0), accentColor.rgb, selectedAmount * 0.28);
    alpha = clamp(alpha * coverage, 0.0, 0.75);
    fragColor = vec4(hue * alpha, alpha) * qt_Opacity;
}
