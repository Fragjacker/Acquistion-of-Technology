Includes = {
	"constants.fxh"
	"vertex_structs.fxh"
	"standardfuncsgfx.fxh"
	"shadow.fxh"
	"tiled_pointlights.fxh"
	"pdxmesh_samplers.fxh"
}

PixelShader =
{
	MainCode PixelAotFakePortal
	ConstantBuffers = {
		Common
		ShipConstants
		Shadow
	}
	[[
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			// Portal parameters (hardcoded since materials don't expose custom float sliders)
			float  RoomDepth  = 1.2;
			float3 EdgeColor  = float3( 0.1, 0.75, 1.0 );
			float  EdgeGlow   = 3.5;
			float  SwirlSpeed = 1.5;

			// 1. Center UVs from [0, 1] to [-1, 1]
			float2 centeredUV     = In.vUV0 * 2.0 - 1.0;
			float  distFromCenter = length( centeredUV );
			clip( 1.0 - distFromCenter );

			// 2. Ray-Box Intersection Math (Fake 3D Depth)
			//    Transform the World View Vector into Tangent Space.
			float3 vNormal      = normalize( In.vNormal );
			float3 vTangent     = normalize( In.vTangent );
			float3 vBitangent   = normalize( In.vBitangent );
			float3 vWorldViewDir = vCamPos.xyz - In.vPos.xyz;
			float3 viewDir = normalize( float3(
				dot( vWorldViewDir, vTangent ),
				dot( vWorldViewDir, vBitangent ),
				dot( vWorldViewDir, vNormal )
			) );

			float3 rayDir    = float3( -viewDir.x, -viewDir.y, viewDir.z * RoomDepth );
			float3 rayOrigin = float3( centeredUV.x, centeredUV.y, -1.0 );

			float3 boxMin = float3( -1.0, -1.0, -1.0 );
			float3 boxMax = float3(  1.0,  1.0,  1.0 );
			float3 t1     = ( boxMin - rayOrigin ) / rayDir;
			float3 t2     = ( boxMax - rayOrigin ) / rayDir;
			float3 tMax   = max( t1, t2 );
			float  t      = min( min( tMax.x, tMax.y ), tMax.z );

			// 3. Sample the Cubemap (engine environment cubemap; see header note)
			float3 hitPos        = rayOrigin + rayDir * t;
			float4 interiorColor = texCUBE( EnvironmentMap, float4( hitPos, 0.0 ) );

			// 4. Procedural Swirling Rim using vanilla time
			float angle   = atan2( centeredUV.y, centeredUV.x );
			float wave    = sin( angle * 6.0 + HdrRange_Time_ClipHeight.y * SwirlSpeed ) * 0.04;
			float rimMask = smoothstep( 0.72 + wave, 0.98, distFromCenter );

			float3 finalRGB   = lerp( interiorColor.rgb, EdgeColor * EdgeGlow, rimMask );
			float  finalAlpha = smoothstep( 1.0, 0.95, distFromCenter );

			finalRGB *= vBloomFactor;

			return float4( finalRGB, finalAlpha );
		}
	]]
}
