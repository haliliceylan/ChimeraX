var data = [["clear_all"], ["create_program", [1, "#ifdef GL_ES\nprecision mediump float;\n#endif\n\n//#define USE_FOG 1\n//#define USE_CLIP_VERTEX 1\n//#define USE_BUILTIN_MATRICES 1\n//#define USE_BUILTIN_VERTEX 1\n\n#ifdef USE_BUILTIN_MATRICES\n#define ProjectionMatrix gl_ProjectionMatrix\n#define ModelViewMatrix gl_ModelViewMatrix\n#define NormalMatrix gl_NormalMatrix\n#else\nuniform mat4 ProjectionMatrix;\nuniform mat4 ModelViewMatrix;\nuniform mat3 NormalMatrix;\n#endif\n\nvarying vec3 N;\nvarying vec3 v;\nvarying vec4 fcolor;\n\n#ifdef USE_BUILTIN_VERTEX\n#define position gl_Vertex\n#else\nattribute vec4 position;\n#endif\nattribute vec3 normal;\nattribute vec4 color;\nattribute mat4 instanceTransform;\nattribute vec3 instanceScale;\n\nvoid main(void)\n{\n  vec3 vi = vec3(vec4(instanceScale * vec3(position), 1) * instanceTransform);\n  v = vec3(ModelViewMatrix * vec4(vi, position.w));\n  N = normalize(NormalMatrix * vec3(vec4(normal,0) * instanceTransform));\n\n  gl_Position = ProjectionMatrix * vec4(v, 1.0);\n  fcolor = color;\n\n#ifdef USE_FOG\n  gl_FogFragCoord = abs(v.z);\n#endif\n\n#ifdef USE_CLIP_VERTEX\n  gl_ClipVertex = ModelViewMatrix * vec4(vi, position.w);\n#endif\n}\n", "#ifdef GL_ES\nprecision mediump float;\n#endif\n\n#define USE_TWO_SIDED_LIGHTING 1\n#define USE_ANGLE_DEPENDENT_TRANSPARENCY 1\n//#define USE_FOG 1\n\nuniform vec4 KeyPosition;\nuniform vec4 FillPosition;\nuniform vec4 BackPosition;\nuniform vec4 KeyDiffuse;\nuniform vec4 FillDiffuse;\nuniform vec4 BackDiffuse;\nuniform vec4 KeySpecular;\nuniform float Shininess;\nuniform vec4 Ambient;\n\nuniform float fogEnabled;\n\nvarying vec3 N;\nvarying vec3 v;\nvarying vec4 fcolor;\n\nvoid main (void)\n{\n  vec3 N1 = normalize(N);\n  vec3 L = normalize(KeyPosition.xyz);  // Light at infinity.\n  vec3 Lf = normalize(FillPosition.xyz); // Light at infinity.\n  vec3 Lb = normalize(BackPosition.xyz); // Light at infinity.\n  vec3 E = normalize(-v);      // In eye coordinates eye position is (0,0,0).\n#ifdef USE_TWO_SIDED_LIGHTING\n  N1 *= (gl_FrontFacing ? 1.0 : -1.0);\n#else\n  if (!gl_FrontFacing) discard;\n#endif\n  vec3 R = normalize(-reflect(L,N1)); \n\n  // diffuse\n  vec4 Idiff = fcolor * (KeyDiffuse * max(dot(N1, L), 0.0)\n                         + FillDiffuse * max(dot(N1, Lf), 0.0)\n                         + BackDiffuse * max(dot(N1, Lb), 0.0));\n\n  // specular\n  vec4 Ispec = KeySpecular * pow(max(dot(R, E), 0.0), 0.3 * Shininess);\n\n  // scene\n  vec4 Iscene = fcolor * Ambient;\n\n  // transparency\n  float a = fcolor.a;\n#ifdef USE_ANGLE_DEPENDENT_TRANSPARENCY\n  a = 1.0 - pow(max(1.0 - a, 0.0), 1.0 / max(abs(N1.z), 0.01));\n#endif\n\n  // total color\n  vec3 Ifrag = Iscene.rgb + Idiff.rgb + Ispec.rgb;\n\n#ifdef USE_FOG\n  // fog\n  float fog = clamp((gl_FogFragCoord - gl_Fog.start) * gl_Fog.scale, 0.0, 1.0);\n  Ifrag = mix(Ifrag, gl_Fog.color.rgb, fogEnabled * fog);\n#endif\n\n  // final color\n  gl_FragColor = vec4(Ifrag, a);\n}\n"]], ["create_singleton", [1, [true, 16, [1062392531, 1060418741, 1057787021, 1065353216]]]], ["create_matrix", [1, [1.0, 0.0, 0.0, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0], false]], ["add_sphere", [1, 0.3520000033378601, 1, 1, [["color", 1, 0, 0, 4, 6, false]], "position", "normal"]], ["create_singleton", [2, [true, 16, [1062392531, 1060418741, 1057787021, 1065353216]]]], ["create_matrix", [2, [1.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0], false]], ["add_sphere", [2, 0.3520000033378601, 1, 2, [["color", 2, 0, 0, 4, 6, false]], "position", "normal"]], ["create_singleton", [3, [true, 16, [1062392531, 1060418741, 1057787021, 1065353216]]]], ["create_matrix", [3, [6.123031769111886e-17, 1.0, 0.0, 0.0, -1.0, 6.123031769111886e-17, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0], false]], ["add_cylinder", [3, 0.20000000298023224, 1.0, 1, 3, [["color", 3, 0, 0, 4, 6, false]], "position", "normal"]], ["set_uniform", [0, "Ambient", 11, [true, 16, [1045019230, 1045019230, 1045019230, 1065353216]]]], ["set_uniform", [0, "FillDiffuse", 11, [true, 16, [1054682907, 1054682907, 1054682907, 1065353216]]]], ["set_uniform", [0, "FillPosition", 11, [true, 16, [1048609554, 1048609554, 1064262697, 0]]]], ["set_uniform", [0, "KeyDiffuse", 11, [true, 16, [1061091803, 1061091803, 1061091803, 1065353216]]]], ["set_uniform", [0, "KeySpecular", 11, [true, 16, [1065353216, 1065353216, 1065353216, 1065353216]]]], ["set_uniform", [0, "KeyPosition", 11, [true, 16, [3199649972, 1059648963, 1059648963, 0]]]], ["set_uniform", [0, "Shininess", 8, [true, 4, [1106247680]]]], ["set_clear_color", [0.5, 0.2, 0.2, 0]], ["set_uniform", [0, "ProjectionMatrix", 14, [true, 64, [1090704579, 0, 0, 0, 0, 1090647796, 0, 0, 0, 0, 3245991580, 3212836864, 0, 0, 3289031486, 0]]]], ["set_uniform", [0, "ModelViewMatrix", 14, [true, 64, [1065353216, 0, 2147483648, 0, 2147483648, 1065353216, 2147483648, 0, 0, 0, 1065353216, 0, 2147483648, 2147483648, 3255737116, 1065353216]]]], ["set_uniform", [0, "NormalMatrix", 13, [true, 36, [1065353216, 0, 2147483648, 2147483648, 1065353216, 2147483648, 0, 0, 1065353216]]]]]
