# Stellaris PDXMESH Shader Authoring (vanilla gfx/FX)

Condensed playbook for writing game-compatible custom pixel shaders for
Stellaris entities (ships/planets), distilled from the vanilla `gfx/FX` files.
Reference mod implementation: `acquistion_of_technology/gfx/FX/`
(`pdxmesh.shader` + `aot_shaders.fxh`, effects `AotPortal*`).

## When to use

Any task that adds or edits a `MainCode` pixel shader, `Effect` block,
sampler or constant buffer for an entity mesh (portals, shields, custom
materials). Also when debugging "erroneous token" errors from
`log/error.log` that do not point at HLSL syntax.

## CRITICAL: comment placement (the #1 gotcha)

**Never put `//` comments in the global (script) namespace of a `.fxh`/`.shader`
file.** The PDX script parser does not strip them correctly and they leak into
the HLSL compile as garbage tokens → "erroneous token" entries in
`log/error.log`.

- `//` HLSL comments: ONLY inside `[[ ... ]]` code blocks.
- `#` comments: the script-namespace comment style used by vanilla
  (`constants.fxh` header, `#SEntityCustomDataInstance` etc.) — keep any
  global-namespace notes on `#` lines, or better, inside code blocks.
- Evidence: across ALL vanilla `gfx/FX` files, only `defines_glsl.fxh`
  (file header) and `pdxmesh_ship.fxh` (inside `ConstantBuffer {}`) have
  script-namespace comments. Every `MainCode`-only file has zero.
- Real incident: the AotPortalCubemap banner (9 `//` lines) sat in the global
  namespace between two `MainCode` blocks in `aot_shaders.fxh`; moved it
  inside `[[ ... ]]` to fix.
- Audit command (must print nothing for your file):
  `awk '/\[\[/{inmain=1} /]]/{inmain=0} !inmain && /\/\// {print FILENAME" L"FNR}' FILE`
  (Caveat: `//` inside `ConstantBuffer {}` bodies appears to be tolerated —
  that is where vanilla does it — but treat it as untested; avoid anyway.)

## File layout / how a mod ships shaders

- The mod **replaces** `gfx/FX/pdxmesh.shader` with a full copy of the vanilla
  one (vanilla path: `D:/SteamLibrary/steamapps/common/Stellaris/gfx/FX/`),
  then appends its own fxh to `Includes = { ... }` at the top (vanilla list
  order preserved, e.g. `"aot_shaders.fxh"` after `"utils.fxh"`).
- All custom code lives in the mod's own `.fxh` (here `aot_shaders.fxh`);
  `pdxmesh.shader` only gains `Effect` blocks that reference the MainCode
  endpoints.
- Includes order matters only in that the file must exist; vanilla already
  pulls in `standardfuncsgfx.fxh`, `vertex_structs.fxh`, `constants.fxh`,
  `tiled_pointlights.fxh`, `shadow.fxh`, `utils.fxh`.

## MainCode template (copy from `pdxmesh_astral_rift.fxh`)

```
MainCode PixelMyEffect
	ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		// //comments are fine IN HERE
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			...
			return float4( 1.0f, 1.0f, 1.0f, 1.0f );
		}
	]]
```

- `ConstantBuffers = { Common, ShipConstants, Shadow }` — Common is the
  generic one (ViewProjectionMatrix, vCamPos, vCamRightDir/LookAtDir/UpDir,
  HdrRange_Time_ClipHeight, SystemLight*, AmbientDiffuse,
  CubemapIntensity, CamLightDiffuse[3], RimLightDiffuse — see
  `standardfuncsgfx.fxh` L5-20); ShipConstants carries entity data
  (PrimaryColor, vBloomFactor, vUVAnimationDir/Time, ...).
- Pixel input struct is `VS_OUTPUT_PDXMESHSTANDARD` (NOT `VS_OUTPUT_PDXMESH`):
  vPosition, vNormal, vTangent, vBitangent, vUV0, vUV1, vPos (world pos),
  vSphere (local pos), vObjectNormal — `vertex_structs.fxh` L25.
- Shadow passes must be `VS_OUTPUT_PDXMESHSHADOW` + `Defines = { "IS_SHADOW" }`
  if you write a custom shadow pixel shader (we instead reuse
  `PixelPdxMeshStandardShadow`).
- Keep vanilla formatting: `MainCode` one tab in, `ConstantBuffers`/`[[`/`]]`
  one tab in, code one tab deeper (verified: every vanilla .fxh indents
  `MainCode` with exactly one tab — `cat -A` shows `^IMainCode`).

## Effect block: always register the 4 variants

```
Effect MyEffect            { VertexShader = "VertexPdxMeshStandard";      PixelShader = "PixelMyEffect"; ... }
Effect MyEffectSkinned     { VertexShader = "VertexPdxMeshStandardSkinned"; PixelShader = "PixelMyEffect"; ... }
Effect MyEffectShadow      { VertexShader = "VertexPdxMeshStandardShadow";      PixelShader = "PixelPdxMeshStandardShadow"; Defines = { "IS_SHADOW" } }
Effect MyEffectSkinnedShadow { VertexShader = "VertexPdxMeshStandardSkinnedShadow"; PixelShader = "PixelPdxMeshStandardShadow"; Defines = { "IS_SHADOW" } }
```

State names (verified occurrences in vanilla pdxmesh.shader):
- BlendState: `BlendStateAlphaBlend` (63×), `BlendStateAdditiveBlend` (31×),
  `BlendStateAlphaBlendWriteAlpha`, `BlendStateAdditiveBlendNoAlpha`,
  `BlendStateAlphaShadow`
- RasterizerState: `RasterizerStateNoCulling`, `RasterizerStateBack`
- DepthStencilState: `DepthStencilNoZWrite` (86×), `DepthStencilNoZ`

Portal-style (semi-transparent, no culling, no Z write) =
`BlendStateAlphaBlend` + `RasterizerStateNoCulling` + `DepthStencilNoZWrite`.

## Samplers available on the pdxmesh pipeline (`pdxmesh_samplers.fxh`)

Index → name: 0 DiffuseMap, 1 SpecularMap, 2 NormalMap, 3 FlagMap,
**4 EnvironmentMap (Type = "Cube")**, 5 LightIndexMap, 6 LightDataMap,
7 LavaNoise (Cube), 8 LavaDiffuse, 9 StoneDiffuse, 10 CustomTexture,
11 CustomTexture2, 12–15 Portrait*.
Cubemap portal trick: bind a cubemap DDS (vanilla:
`gfx/worldgfx/cubemap_filtered_ldr.dds`) to the entity's EnvironmentMap slot
and `texCUBE( EnvironmentMap, dir )` from the pixel shader.

## Game-compatible HLSL (what vanilla actually targets)

- The pipeline compiles HLSL for DX9/DX10/11 and GLSL paths. Write
  SM3/SM4-safe HLSL: use `float2/3/4`, `float4x4`, `tex2D`, `texCUBE`,
  `tex2Dlod`, `texCUBElod`, `texCUBEbias` (all present in vanilla).
- `defines_glsl.fxh` shows the compatibility shims (`tex2Dbias`/`tex2Dgrad`
  fall back to `tex2Dlod0` on the GL path) — don't rely on SM5+ features
  (no texture fetch at arbitrary lod + derivatives mixes, no
  `SV_` semantics — output semantic is `PDX_COLOR`).
- Loops: if the bound is not a compile-time constant add `[unroll]`
  (`#ifdef PDX_DIRECTX_9` guard in vanilla pdxmesh.shader ~L1412).
- `#define static` exists for the GL path → plain `static const float X = ...;`
  is the right way to declare shader constants (constants.fxh pattern).
- **NEVER use a vector conditional (ternary) — e.g. `( v >= 0.0f ) ? a : b`
  where `v`/`a`/`b` are `float2/3/4`.** HLSL has no 3-component vector
  conditional operator and the PDX translator rejects the whole pixel shader
  (`pdxshaderparser.cpp:1436: Failed adding pixel shader gfx/FX/pdxmesh.shader(…)`,
  surfacing as the generic `X3014: incorrect number of arguments to
  numeric-type constructor`). No vanilla shader uses a vector ternary.
  - Replace with `step()` + `lerp()`: `lerp( A, B, step( 0.0, V ) )` selects
    `A` where `V<0` and `B` where `V>=0` — component-wise, no branches.
    (`step` is a native GLSL+HLSL builtin; `lerp` is `#define lerp mix` on the
    GL path — `defines_glsl.fxh` L94. Scalar ternaries are fine.)
  - Real incident: `AotPortalCubemap` used
    `( rd >= 0.0f ) ? float3(1) : float3(0)` in the ray-box `tMax` select;
    the shader failed to load and the portal fell back to a default. Fixed
    with `float3 sel = step(0.0, rd); lerp( -1-ro, 1-ro, sel );`
- Reusable helpers already exist — prefer them: `ApplyDissolve`
  (pdxmesh_ship.fxh, uses CustomTexture2+PrimaryColor), `VoronoiNoise2D`,
  ToGamma/ToLinear, Rand2DTo1D, pointlight accumulation
  (`standardfuncsgfx.fxh`, `tiled_pointlights.fxh`).
- Tunable numbers belong in `constants.fxh`-style `static const` blocks, not
  hard-coded (vanilla convention; updatable via `reloadfx all`).

## Verification loop (no offline compiler here)

1. Static: run the awk comment audit above on every touched file; grep that
   every `Effect` references a MainCode that exists and vice versa
   (`grep -n "MainCode\|^Effect" pdxmesh.shader`).
2. In game: `reloadfx all` console command recompiles shaders without
   restart (per `constants.fxh` header). Then check
   `D:/SteamLibrary/steamapps/common/Stellaris/log/error.log` for
   "erroneous token" / compile lines; place any suspect comment and watch
   for the token leak to confirm the global-namespace rule.
3. In this sandbox the Steam path is mounted under `D:/` (git-bash) but NOT
   a writable workspace target — read-only reference is fine; all edits go
   under `acquistion_of_technology/`.

## Checklist before shipping a shader change

- [ ] No `//` comments in global namespace (awk audit passes)
- [ ] `MainCode` + 4 `Effect` variants (plain/Skinned/Shadow/SkinnedShadow)
- [ ] Correct input struct (`VS_OUTPUT_PDXMESHSTANDARD` / `...SHADOW`)
- [ ] Output `: PDX_COLOR`, returns premultiplied-ready `float4`
- [ ] Loop bounds constant or `[unroll]`ed
- [ ] Only sampler names from `pdxmesh_samplers.fxh`
- [ ] `acquistion_of_technology/gfx/FX/aot_shaders.fxh` is in the `Includes`
      list of the mod's `pdxmesh.shader`
- [ ] `reloadfx all` in game, `log/error.log` clean, effect visible
