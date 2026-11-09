Includes = {
	"constants.fxh"
	"pdxmesh_samplers.fxh"
	"shadow.fxh"
	"standardfuncsgfx.fxh"
	"tiled_pointlights.fxh"
	"vertex_structs.fxh"
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

	MainCode PixelAotPortal
		ConstantBuffers = { Common, ShipConstants, Shadow }
	[[
		// --- procedural noise (replaces the external "noise texture") ---------
		float AotHash21( float2 aP )
		{
			return frac( sin( dot( aP, float2( 12.9898f, 78.233f ) ) ) * 43758.5453f );
		}

		float AotValueNoise( float2 aP )
		{
			float2 aCell = floor( aP );
			float2 aFrac = aP - aCell;
			float2 aU    = aFrac * aFrac * ( 3.0f - 2.0f * aFrac );   // smoothstep
			float aA = AotHash21( aCell );
			float aB = AotHash21( aCell + float2( 1.0f, 0.0f ) );
			float aC = AotHash21( aCell + float2( 0.0f, 1.0f ) );
			float aD = AotHash21( aCell + float2( 1.0f, 1.0f ) );
			return lerp( lerp( aA, aB, aU.x ), lerp( aC, aD, aU.x ), aU.y );
		}

		float AotFbm( float2 aP, int aOct )
		{
			float aSum  = 0.0f;
			float aAmp  = 0.5f;
			float aFreq = 1.0f;
			for ( int i = 0; i < aOct; i++ )
			{
				aSum += aAmp * AotValueNoise( aP * aFreq );
				aFreq *= 2.0f;
				aAmp  *= 0.5f;
			}
			return aSum;
		}

		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			const float AotPI = 3.14159265f;
			float  vTime   = HdrRange_Time_ClipHeight.y;      // vanilla time (s)
			float2 vUv     = In.vUV0;
			float2 vD      = vUv - float2( 0.5f, 0.5f );
			float  vR      = length( vD );                     // Polar Coordinates.R
			float  vAngle  = atan2( vD.y, vD.x );               // Polar Coordinates.G (angle)

			// --- inward suction: R offset by time (Add node) --------------------
			float vSuck   = vR - vTime * 0.25f;

			// --- spiral: A offset by R (further out rotates more) ---------------
			float vSpiral = vAngle + vR * AotPI * 2.0f * 3.0f;

			// --- polar UV fed to the (procedural) noise texture -----------------
			//     X = (R - time)  -> pulls the noise inwards
			//     Y = (A + R*k)   -> spirals the noise
			float2 vPolarUV = float2( vSuck * 3.0f, vSpiral * 1.0f );

			// --- sample the noise texture (animated via a 2nd time scroll) -----
			float vNoise = AotFbm( vPolarUV + vTime * float2( 0.10f, 0.04f ), 4 );

			// --- wobbling edge: small animated noise added to the radius --------
			float vEdgeNoise = AotFbm( vUv * 4.0f + vTime * 0.20f, 3 ) * 0.15f;
			float vWobR      = vR + vEdgeNoise;

			// --- circular clip (Step node + AlphaClipThreshold 0.5) -------------
			float vClip = 1.0f - smoothstep( 0.98f, 1.0f, vWobR );

			// --- color: HDR color * noise ^ 3 (Power node = 3, HDR intensity 3) -
			float3 vLow  = HSVtoRGB( float3( 3.9, 0.9f, 1.0f ) );   // violet
			float3 vHigh = HSVtoRGB( float3( 3.8f, 0.95f, 1.0f ) );   // blue-cyan
			float3 vHue  = lerp( vLow, vHigh, saturate( vNoise ) );
			float3 vColor = vHue * pow( saturate( vNoise * 1.3f ), 3.0f ) * 3.0f;

			// soften the very center so the "mouth" is not a hard hole
			vColor *= smoothstep( 0.0f, 0.12f, vR );

			vColor *= vClip;
			vColor *= vBloomFactor;

			// Additive blend state => pure black == fully transparent
			return float4( vColor, 1.0f );
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