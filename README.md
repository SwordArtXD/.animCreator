# .animCreator

## Overview
This app lets you export animations or actions from an FBX file—whether exported from Blender or MAYA—into .anim format. You can choose to export individual animations or export them all at once by selecting the "Export All Animations" button. Additionally, you can right-click on an animation to delete, rename, or export it individually.

## Using Blender

### 1. Frame Rate Setting
Ensure the frame rate in the Output tab of Blender’s properties editor is set to **30 FPS**. This will help maintain the animation’s original frame count and prevent any time-stretching.

### 2. Clean Up Unused Bones
Before exporting, make sure only the bones with actual animation data are present. Even if a bone doesn't have keyframes in Blender, the app will still generate them. To avoid this, you might want to create different Blend files tailored to your needs. Also, verify that no keyframe data exists for bones you’ve deleted. You can remove unwanted keyframes by clicking on the empty space in your scene and deleting them via the Dope Sheet. (Otherwise, the animations may not appear in the app.)

### 3. FBX Export Settings
When exporting to FBX, go to the **Include** section and select only the armature. Skip the next section and proceed to **Armature**, where you should uncheck "Add Leaf Bones." Then, under the **Animation** section, uncheck "NLA Strips" and set the **Simplify** value to 0.

## Conclusion
Once set up, the process is straightforward. If you encounter any bugs or have questions, feel free to reach out. If you’d like to contribute improvements to the software, DM me on Discord at **kb0mbyolo**!
