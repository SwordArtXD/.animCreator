from fbx import FbxManager, FbxScene, FbxImporter, FbxAnimStack, FbxCriteria

def load_fbx_animations(fbx_file):
    """
    Load animations from an FBX file and rename them to remove '|' and their prefixes.

    Args:
        fbx_file (str): Path to the FBX file.

    Returns:
        tuple: A tuple containing a list of tuples with original and cleaned animation names, and the FBX scene.
    """
    manager = FbxManager.Create()
    importer = FbxImporter.Create(manager, "")
    scene = FbxScene.Create(manager, "Scene")

    if not importer.Initialize(fbx_file, -1, manager.GetIOSettings()):
        raise Exception(f"Failed to initialize FBX importer for file: {fbx_file}")

    if not importer.Import(scene):
        raise Exception(f"Failed to import FBX file: {fbx_file}")

    importer.Destroy()

    # Use FbxCriteria to get the animation stack count
    anim_stack_count = scene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))

    animations_with_originals = []
    for i in range(anim_stack_count):
        anim_stack = scene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), i)
        original_name = anim_stack.GetName()
        cleaned_name = clean_animation_name(original_name)
        anim_stack.SetName(cleaned_name)  # Rename the animation in memory
        animations_with_originals.append((original_name, cleaned_name))

    return animations_with_originals, scene

def clean_animation_name(name):
    """
    Cleans the animation name by removing everything before and including the '|'.
    
    Args:
        name (str): The original name of the animation.
    
    Returns:
        str: The cleaned animation name.
    """
    if '|' in name:
        return name.split('|', 1)[-1]  # Split at '|' and return the part after it
    return name

