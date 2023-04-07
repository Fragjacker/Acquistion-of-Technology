Includes = {
	"constants.fxh"
	"vertex_structs.fxh"
	"standardfuncsgfx.fxh"
	"shadow.fxh"
	"tiled_pointlights.fxh"
	"pdxmesh_samplers.fxh"
	"pdxmesh_ship.fxh"
}

MainCode PixelAotPlanetShieldDM
		ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float3 RimColor = HSVtoRGB( float3( 2.3f, 1.0f, 1.0f ) );
			const float RimAlpha = 0.15f;
			const float vRimStart = 0.75f;
			const float vRimStop = 0.5f;

			// Normal
			float3 vInNormal = normalize( In.vNormal );
			float4 vNormalMap = tex2D( NormalMap, In.vUV0 );
			float3 vNormalSample = UnpackRRxGNormal(vNormalMap);

			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize(mul( vNormalSample, TBN ));

			float vDot = dot( vNormal, -vCamLookAtDir );

			float vRim = smoothstep( vRimStart, vRimStop, abs( vDot ) );
			float4 vColor = vRim * float4( RimColor.rgb, RimAlpha );
			if( vDot > 0.f )
			{
				float vTime = ( vUVAnimationTime + HdrRange_Time_ClipHeight.y ) * 0.15f;
				vColor += tex2D( DiffuseMap, In.vUV0 + vUVAnimationDir * vTime );
				vColor += tex2D( DiffuseMap, ( In.vUV0 + float2( 0.20f, -0.13f ) * vTime * 0.27f ) );
			}

			float3 vEyeDir = normalize( In.vPos.xyz - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, In.vNormal );
			float pulse = ( 0.9f + 0.1f * sin( 3.141f * length( texCUBElod( EnvironmentMap, float4(reflection, 0) ).rgb ) + HdrRange_Time_ClipHeight.y * 1.f - In.vSphere.z * In.vSphere.y * 0.125f ) );
			vColor += pow( pulse, 40.0f ) * 0.1f;

			vColor.rgb = ApplyDissolve( PrimaryColor.rgb, ShipVars.b, vColor.rgb, RimColor, In.vUV0 );

			vColor.rgb *= vBloomFactor;
			return vColor;
		}
	]]

	MainCode PixelAotPlanetShieldAE
		ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float3 RimColor = HSVtoRGB( float3( 3.8f, 1.0f, 1.0f ) );
			const float RimAlpha = 0.35f;
			const float vRimStart = 1.0f;
			const float vRimStop = 0.5f;

			// Normal
			float3 vInNormal = normalize( In.vNormal );
			float4 vNormalMap = tex2D( NormalMap, In.vUV0 );
			float3 vNormalSample = UnpackRRxGNormal(vNormalMap);

			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize(mul( vNormalSample, TBN ));

			float vDot = dot( vNormal, -vCamLookAtDir );

			float vRim = smoothstep( vRimStart, vRimStop, abs( vDot ) );
			float4 vColor = vRim * float4( RimColor.rgb, RimAlpha );
			if( vDot > 0.f )
			{
				float vTime = ( vUVAnimationTime + HdrRange_Time_ClipHeight.y ) * 0.15f;
				vColor += tex2D( DiffuseMap, In.vUV0 + vUVAnimationDir * vTime );
				vColor += tex2D( DiffuseMap, ( In.vUV0 + float2( 0.20f, -0.13f ) * vTime * 0.27f ) );
			}

			float3 vEyeDir = normalize( In.vPos.xyz - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, In.vNormal );
			float pulse = ( 0.9f + 0.1f * sin( 3.141f * length( texCUBElod( EnvironmentMap, float4(reflection, 0) ).rgb ) + HdrRange_Time_ClipHeight.y * 1.f - In.vSphere.z * In.vSphere.y * 0.125f ) );
			vColor += pow( pulse, 40.0f ) * 0.1f;

			vColor.rgb = ApplyDissolve( PrimaryColor.rgb, ShipVars.b, vColor.rgb, RimColor, In.vUV0 );

			vColor.rgb *= vBloomFactor;
			return vColor;
		}
	]]

	MainCode PixelAotPlanetShieldStellarite
		ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float3 RimColor = HSVtoRGB( float3( 0.3f, 1.0f, 1.0f ) );
			const float RimAlpha = 0.35f;
			const float vRimStart = 1.0f;
			const float vRimStop = 0.5f;

			// Normal
			float3 vInNormal = normalize( In.vNormal );
			float4 vNormalMap = tex2D( NormalMap, In.vUV0 );
			float3 vNormalSample = UnpackRRxGNormal(vNormalMap);

			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize(mul( vNormalSample, TBN ));

			float vDot = dot( vNormal, -vCamLookAtDir );

			float vRim = smoothstep( vRimStart, vRimStop, abs( vDot ) );
			float4 vColor = vRim * float4( RimColor.rgb, RimAlpha );
			if( vDot > 0.f )
			{
				float vTime = ( vUVAnimationTime + HdrRange_Time_ClipHeight.y ) * 0.15f;
				vColor += tex2D( DiffuseMap, In.vUV0 + vUVAnimationDir * vTime );
				vColor += tex2D( DiffuseMap, ( In.vUV0 + float2( 0.20f, -0.13f ) * vTime * 0.27f ) );
			}

			float3 vEyeDir = normalize( In.vPos.xyz - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, In.vNormal );
			float pulse = ( 0.9f + 0.1f * sin( 3.141f * length( texCUBElod( EnvironmentMap, float4(reflection, 0) ).rgb ) + HdrRange_Time_ClipHeight.y * 1.f - In.vSphere.z * In.vSphere.y * 0.125f ) );
			vColor += pow( pulse, 40.0f ) * 0.1f;

			vColor.rgb = ApplyDissolve( PrimaryColor.rgb, ShipVars.b, vColor.rgb, RimColor, In.vUV0 );

			vColor.rgb *= vBloomFactor;
			return vColor;
		}
	]]

	MainCode PixelAotPlanetShieldPE
		ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float3 RimColor = HSVtoRGB( float3( 0.0f, 1.0f, 1.0f ) );
			const float RimAlpha = 0.35f;
			const float vRimStart = 1.0f;
			const float vRimStop = 0.5f;

			// Normal
			float3 vInNormal = normalize( In.vNormal );
			float4 vNormalMap = tex2D( NormalMap, In.vUV0 );
			float3 vNormalSample = UnpackRRxGNormal(vNormalMap);

			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize(mul( vNormalSample, TBN ));

			float vDot = dot( vNormal, -vCamLookAtDir );

			float vRim = smoothstep( vRimStart, vRimStop, abs( vDot ) );
			float4 vColor = vRim * float4( RimColor.rgb, RimAlpha );
			if( vDot > 0.f )
			{
				float vTime = ( vUVAnimationTime + HdrRange_Time_ClipHeight.y ) * 0.15f;
				vColor += tex2D( DiffuseMap, In.vUV0 + vUVAnimationDir * vTime );
				vColor += tex2D( DiffuseMap, ( In.vUV0 + float2( 0.20f, -0.13f ) * vTime * 0.27f ) );
			}

			float3 vEyeDir = normalize( In.vPos.xyz - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, In.vNormal );
			float pulse = ( 0.9f + 0.1f * sin( 3.141f * length( texCUBElod( EnvironmentMap, float4(reflection, 0) ).rgb ) + HdrRange_Time_ClipHeight.y * 1.f - In.vSphere.z * In.vSphere.y * 0.125f ) );
			vColor += pow( pulse, 40.0f ) * 0.1f;

			vColor.rgb = ApplyDissolve( PrimaryColor.rgb, ShipVars.b, vColor.rgb, RimColor, In.vUV0 );

			vColor.rgb *= vBloomFactor;
			return vColor;
		}
	]]