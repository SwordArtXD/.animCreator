# .animCreator
This app allows you to export animations/actions from an FBX file exported from blender or even MAYA as a .anim. You can either export single animations or in bulk by selecting the "Export All Animations" Button. You also have the option to delete, rename or export a single animation by right-clicking it.
# In Blender
1. Ensure the Frame Rate in the Output" Tab of the properties editor is set to 30 FPS to avoid stretching your animation and keeping its original frame count.
2. Make sure that only the bones that you wnat animation data on exist! Even if you do not have any keyframe data in Blender, the app will create them. So you may want to duplicate different Blend files to suit your needs. You must also ensure that the animations you want exported do not have keyframe data for the deleted bones. You can delete such data by clicking the empty space of your scen and deleting them in the Dope Sheet.
