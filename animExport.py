import os
from fbx import FbxManager, FbxScene, FbxImporter, FbxAnimStack, FbxCriteria, FbxNode, FbxAnimCurve, FbxAnimCurveKey, FbxAnimLayer, FbxAnimCurveDef, FbxAnimCurveNode, FbxAnimCurveFilter, FbxAnimCurveFilterKeyReducer, FbxAnimCurveFilterConstantKeyReducer, FbxAnimCurveFilterUnroll, FbxAnimCurveFilterTSS, FbxAnimCurveFilterMatrixConverter, FbxAnimCurveFilterResample, FbxAnimCurveFilterKeySync, FbxAnimCurveFilterGimbleKiller, FbxAnimCurveFilterUnroll, FbxAnimCurveFilterConstantKeyReducer, FbxAnimCurveFilterTSS, FbxAnimCurveFilterMatrixConverter, FbxAnimCurveFilterResample, FbxAnimCurveFilterKeySync, FbxAnimCurveFilterGimbleKiller

def find_bone_recursive(node, bone_name):
    """
    Recursively search for a bone by name in the node hierarchy.
    
    Args:
        node (FbxNode): The current FBX node being traversed.
        bone_name (str): The name of the bone to find.
        
    Returns:
        FbxNode: The bone node if found, otherwise None.
    """
    if node.GetName() == bone_name:
        return node

    for i in range(node.GetChildCount()):
        found_node = find_bone_recursive(node.GetChild(i), bone_name)
        if found_node:
            return found_node

    return None

def get_transform_key(transform, axis):
    """
    Get the correct key index for the transform (translate, rotate, scale) and axis (X, Y, Z).
    translateX = 0, translateY = 1, translateZ = 2
    rotateX = 3, rotateY = 4, rotateZ = 5
    scaleX = 6, scaleY = 7, scaleZ = 8
    """
    key_map = {
        'translate': {'X': 0, 'Y': 1, 'Z': 2},
        'rotate': {'X': 3, 'Y': 4, 'Z': 5},
        'scale': {'X': 6, 'Y': 7, 'Z': 8}
    }
    return key_map[transform][axis]

def export_single_animation(anim_original, save_path, scene, original_fps=25, target_fps=25):
    """
    Export a single animation to the specified path in .anim format.
    Args:
        anim_original (str): The original animation name.
        save_path (str): The path to save the exported animation.
        scene (FbxScene): The FBX scene containing the animation.
        original_fps (int): The frame rate of the original animation (default is 25).
        target_fps (int): The desired frame rate of the exported animation (default is 25).
    """
    print(f"Exporting animation: {anim_original} to {save_path}")

    # Find the correct animation stack in the FBX scene
    anim_stack_count = scene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))
    
    for i in range(anim_stack_count):
        anim_stack = scene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), i)

        if anim_stack.GetName() == anim_original:
            print(f"Found animation stack: {anim_original}")

            # Extract keyframe data
            keyframe_data = get_bones_with_keyframes(anim_stack, scene)

            # Skip the first bone entirely (assumed to be the armature)
            if len(keyframe_data) > 1:
                keyframe_data = keyframe_data[1:]  # Exclude the first bone in the list

            # Collect all keyframe times to determine start and end times
            all_keyframe_times = [kf['time'] for _, bone_keyframes in keyframe_data for kf in bone_keyframes]

            if all_keyframe_times:
                start_time = 0  # First frame should always be 0
                end_time = max(all_keyframe_times)  # Use the max frame as the end time
                print(f"Calculated frame range: start_time={start_time}, end_time={end_time}")

                # If frame rate conversion is needed
                if original_fps != target_fps:
                    scale_factor = original_fps / target_fps
                    print(f"Scaling keyframes by factor: {scale_factor}")
                    for bone_name, bone_keyframes in keyframe_data:
                        for keyframe in bone_keyframes:
                            keyframe['time'] = int(keyframe['time'] * scale_factor)
            else:
                start_time = 0
                end_time = 0

            # Write the data to the .anim file
            with open(save_path, 'w') as file:
                # Write basic headers
                file.write("animVersion 1.1;\n")
                file.write("mayaVersion 2025;\n")
                file.write("timeUnit pal;\n")  # Make sure it uses 'pal' for 25 FPS
                file.write("linearUnit cm;\n")
                file.write("angularUnit deg;\n")
                file.write(f"startTime {start_time};\n")
                file.write(f"endTime {end_time};\n")

                # Export keyframes for each bone and transform
                for bone_name, bone_keyframes in keyframe_data:
                    bone = scene.FindNodeByName(bone_name)

                    for transform in ['translate', 'rotate', 'scale']:
                        for axis in ['X', 'Y', 'Z']:
                            # Filter keyframes by curve
                            axis_keyframes = [kf for kf in bone_keyframes if kf['curve'] == f"{transform}{axis}"]

                            if axis_keyframes:
                                file.write(f"anim {transform}.{transform}{axis} {transform}{axis} {bone_name} 0 {bone.GetChildCount()} {get_transform_key(transform, axis)};\n")
                                file.write("animData {\n")
                                file.write("  input time;\n")
                                file.write("  output linear;\n")
                                file.write("  weighted 0;\n")
                                file.write("  preInfinity constant;\n")
                                file.write("  postInfinity constant;\n")

                                file.write("  keys {\n")
                                for idx, keyframe in enumerate(axis_keyframes):
                                    time = int(keyframe['time'])  # Ensure correct timing based on frame rate
                                    value = keyframe['value']
                                    if value.is_integer():
                                        value = int(value)

                                    # Write keyframe
                                    if idx == 0:
                                        file.write(f"    {time} {value} fixed fixed 1 0 0 0 1 0 1;\n")
                                    else:
                                        file.write(f"    {time} {value} linear linear 1 0 0;\n")

                                file.write("  }\n")
                                file.write("}\n")

    print(f"Animation {anim_original} exported successfully.")

def export_all_animations(animations, export_dir, scene, original_fps=25, target_fps=25):
    """
    Export all animations to the specified directory.

    Args:
        animations (list): List of animation names to export.
        export_dir (str): Directory to save the exported animations.
        scene (FbxScene): The FBX scene containing the animations.
        original_fps (int): Original FPS of animations.
        target_fps (int): Desired FPS of exported animations.
    """
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)  # Ensure the directory exists
    
    for anim in animations:
        save_path = os.path.join(export_dir, f"{anim}.anim")

        # Ensure that each animation starts fresh with its own keyframe data
        print(f"Starting export for animation: {anim}")
        export_single_animation(anim, save_path, scene, original_fps, target_fps)

    print("All animations exported successfully!")

def get_animation_keyframes(anim_stack, scene):
    """
    Extracts keyframe data from the animation stack and scene.

    Args:
        anim_stack (FbxAnimStack): The animation stack containing the animation data.
        scene (FbxScene): The FBX scene containing the animation and bone structure.

    Returns:
        List[dict]: A list of keyframe data for each bone in the scene.
    """
    bones_with_keyframes = []

    # Print the animation stack name for debugging
    print(f"Using animation stack: {anim_stack.GetName()}")

    # Get the first animation layer from the stack
    anim_layer = anim_stack.GetMember(FbxAnimLayer.ClassId, 0)
    if not anim_layer:
        print(f"No animation layers found in stack: {anim_stack.GetName()}")
        return []

    # Print the animation layer name for debugging
    print(f"Using animation layer: {anim_layer.GetName()}")

    # Iterate through all nodes in the scene to find bones with animation data
    node_count = scene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxNode.ClassId))
    
    for i in range(node_count):
        node = scene.GetSrcObject(FbxCriteria.ObjectType(FbxNode.ClassId), i)
        bone_name = node.GetName()

        print(f"Checking bone: {bone_name}")

        # Pass both the node and the anim_layer to the function
        keyframe_data = extract_keyframe_data_from_node(node, anim_layer)  # Correctly pass both arguments
        
        if keyframe_data:
            print(f"Keyframes found for bone: {bone_name}")
            bones_with_keyframes.append((bone_name, keyframe_data))
        else:
            print(f"No keyframes found for bone: {bone_name}")
    
    return bones_with_keyframes

def get_bones_with_keyframes(anim_stack, scene):
    """
    Extract all bones that have keyframe data in the FBX scene.

    Args:
        anim_stack (FbxAnimStack): The animation stack containing the animation data.
        scene (FbxScene): The FBX scene containing the animation and bone structure.

    Returns:
        List[Tuple[str, List[dict]]]: A list of tuples where each tuple contains a bone name and its associated keyframe data.
    """
    bones_with_keyframes = []

    # Print the animation stack name for debugging
    print(f"Using animation stack: {anim_stack.GetName()}")

    # Get the first animation layer from the stack
    anim_layer = anim_stack.GetMember(FbxAnimLayer.ClassId, 0)
    if not anim_layer:
        print(f"No animation layers found in stack: {anim_stack.GetName()}")
        return []

    # Print the animation layer name
    print(f"Using animation layer: {anim_layer.GetName()}")

    # Iterate through all nodes in the scene to find bones with animation data
    node_count = scene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxNode.ClassId))
    
    for i in range(node_count):
        node = scene.GetSrcObject(FbxCriteria.ObjectType(FbxNode.ClassId), i)
        bone_name = node.GetName()

        print(f"Checking bone: {bone_name}")

        # Pass both the node and the anim_layer to the function
        keyframe_data = extract_keyframe_data_from_node(node, anim_layer)
        
        if keyframe_data:
            print(f"Keyframes found for bone: {bone_name}")
            bones_with_keyframes.append((bone_name, keyframe_data))
        else:
            print(f"No keyframes found for bone: {bone_name}")
    
    return bones_with_keyframes


def extract_keyframe_data_from_node(node, anim_layer):
    """
    Extract keyframe data from a node (bone) in the FBX scene.

    Args:
        node (FbxNode): The node (bone) from which to extract keyframe data.
        anim_layer (FbxAnimLayer): The animation layer containing keyframe data.

    Returns:
        List[dict]: A list of keyframe data dictionaries.
    """
    keyframe_data = []

    # Access the animation curves for each transform (translate, rotate, scale) in the current animation layer
    anim_curves = {
        "translateX": node.LclTranslation.GetCurve(anim_layer, 'X'),
        "translateY": node.LclTranslation.GetCurve(anim_layer, 'Y'),
        "translateZ": node.LclTranslation.GetCurve(anim_layer, 'Z'),
        "rotateX": node.LclRotation.GetCurve(anim_layer, 'X'),
        "rotateY": node.LclRotation.GetCurve(anim_layer, 'Y'),
        "rotateZ": node.LclRotation.GetCurve(anim_layer, 'Z'),
        "scaleX": node.LclScaling.GetCurve(anim_layer, 'X'),
        "scaleY": node.LclScaling.GetCurve(anim_layer, 'Y'),
        "scaleZ": node.LclScaling.GetCurve(anim_layer, 'Z'),
    }

    # Iterate through each animation curve and extract keyframe data
    for curve_name, curve in anim_curves.items():
        if curve:  # If the curve exists for this transform
            keyframe_count = curve.KeyGetCount()

            for key_index in range(keyframe_count):
                key = curve.KeyGet(key_index)
                keyframe_data.append({
                    "curve": curve_name,                  # Store which curve (transform + axis) this keyframe belongs to
                    "time": key.GetTime().GetFrameCount(),  # Convert FBX time to frame
                    "value": key.GetValue(),                # Value of the transform at this keyframe
                    "interp_in": "linear",                  # Interpolation type (can adjust based on actual curve data)
                    "interp_out": "linear",                 # Interpolation type (can adjust based on actual curve data)
                    "weight_in": 1,                         # Default weight
                    "weight_out": 1,                        # Default weight
                    "tangent_in": 0,                        # Default tangent
                    "tangent_out": 0                        # Default tangent
                })

    if not keyframe_data:
        print(f"No keyframe data found for node: {node.GetName()}")

    return keyframe_data
