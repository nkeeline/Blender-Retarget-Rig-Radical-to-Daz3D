bl_info = {
    "name": "KeeMap Anicmation Transfer Tool",
    "description": "Tools for moving animation from one Rig To Another",
    "author": "Nick Keeline",
    "version": (0, 0, 0),
    "blender": (2, 83, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Transfer Animation"
}




import bpy
import math
import json
from os import path
import mathutils

def Update():
    #bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    #bpy.context.view_layer.update()
    #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
def SetBonePosition(SourceArmature, SourceBoneName, DestinationArmature, DestinationBoneName, DestinationTwistBoneName, WeShouldKeyframe):
    destination_bone =  DestinationArmature.pose.bones[DestinationBoneName]
    sourceBone = SourceArmature.pose.bones[SourceBoneName]
    
    WsPosition = sourceBone.matrix.translation
    matrix_final = SourceArm.matrix_world @ sourceBone.matrix
    destination_bone.matrix.translation = matrix_final.translation
    #destination_bone.location = sourceBone.location
    Update()
    if (WeShouldKeyframe):
        currentFrame = bpy.context.scene.frame_current
        destination_bone.keyframe_insert(data_path='location',frame=currentFrame)
    
def SetBoneRotation(SourceArmature, SourceBoneName, DestinationArmature, DestinationBoneName, DestinationTwistBoneName, CorrectionQuat, WeShouldKeyframe, hastwistbone):

    #Get the rotation of the bone in edit mode
    SourceBoneEdit = SourceArmature.data.bones[SourceBoneName]
    SourceBoneEditRotation = SourceBoneEdit.matrix_local.to_quaternion()
    
    #Get the rotation of the bone in edit mode
    DestinationBoneEdit = DestinationArmature.data.bones[DestinationBoneName]
    DestinationBoneEditRotation = DestinationBoneEdit.matrix_local.to_quaternion()
    
    DeltaSourceEditBoneandDestEditBone = DestinationBoneEditRotation.rotation_difference(SourceBoneEditRotation)
    DeltaDestinationEditBoneandSourceEdit = SourceBoneEditRotation.rotation_difference(DestinationBoneEditRotation)
    
    #rotate the edit rotation quat first to armature rotation
    #ArmatureSpaceBoneEditPosition = RigArmature.rotation_quaternion * BoneEditRotation
    if(DestinationTwistBoneName != ""):
        TwistBone = DestinationArmature.pose.bones[DestinationTwistBoneName]
    destination_bone =  DestinationArmature.pose.bones[DestinationBoneName]
    sourceBone = SourceArmature.pose.bones[SourceBoneName]
    
    #Set Bone Position now that we've calculated it.
    destination_bone.rotation_mode = 'QUATERNION'
    sourceBone.rotation_mode = 'QUATERNION'
     
     #################################################
     ################## Get Source WS Quat ###########
     #################################################
    source_arm_matrix = SourceArmature.matrix_world
    source_bone_matrix = sourceBone.matrix
    
    #get the source bones rotation in world space.
    source_bone_world_matrix = source_arm_matrix @ source_bone_matrix
    
    SourceBoneRotWS = source_bone_world_matrix.to_quaternion()
    #print('Source Rotation')
    #print(SourceBoneRotWS)
     
     #################################################
     ################## Get Dest edit WS Quat ###########
     #################################################
    dest_arm_matrix = DestinationArmature.matrix_world
    dest_bone_matrix = destination_bone.matrix
    
    #get the DESTINATION bones rotation in world space.
    dest_bone_world_matrix = dest_arm_matrix @ dest_bone_matrix
    
    DestBoneRotWS = dest_bone_world_matrix.to_quaternion()
    #print('Destination Rotation')
    #print(DestBoneRotWS)
    
    DifferenceBetweenSourceWSandDestWS = DestBoneRotWS.rotation_difference(SourceBoneRotWS)
    #print('Difference Rotation')
    #print(DifferenceBetweenSourceWSandDestWS)
    destination_bone.rotation_quaternion = DeltaDestinationEditBoneandSourceEdit @ sourceBone.rotation_quaternion# @ DeltaDestinationEditBoneandSourceEdit.inverted() @ CorrectionQuat
    #destination_bone.rotation_quaternion = destination_bone.rotation_quaternion @ DifferenceBetweenSourceWSandDestWS #@ CorrectionQuat
    
    destination_bone.rotation_mode = 'XYZ'
    sourceBone.rotation_mode = 'XYZ'
    
    Update()
    
    if (hastwistbone):
        TwistBone.rotation_mode = 'XYZ'
        destination_bone.rotation_mode = 'XYZ'
        yrotation = destination_bone.rotation_euler.y
        destination_bone.rotation_euler.y = 0
        TwistBone.rotation_euler.y = yrotation
        #print('Setting Twist Bone: ' + yrotation)
        TwistBone.rotation_mode = 'QUATERNION'
        destination_bone.rotation_mode = 'QUATERNION'
        
    Update()
    
    if (WeShouldKeyframe):
        currentFrame = bpy.context.scene.frame_current
        destination_bone.rotation_mode = 'XYZ'
        destination_bone.keyframe_insert(data_path='rotation_euler',frame=currentFrame)
        #print('keyframed' + str(currentFrame))
        if (hastwistbone):
            TwistBone.rotation_mode = 'XYZ'
            TwistBone.keyframe_insert(data_path='rotation_euler',frame=currentFrame)

def GetBoneEditRotationWorldSpace(arm, bonename):
    BoneEdit = arm.data.bones[bonename]
    BoneEditRotation = BoneEdit.matrix_local.to_quaternion()
    BoneEditWS = arm.rotation_quaternion*BoneEditRotation
    return BoneEditWS

class KeeMapSettings(bpy.types.PropertyGroup):

    start_frame_to_apply: bpy.props.IntProperty(
        name = "Starting Frame",
        description="Frame to Apply Motion Capture To",
        default = 0,
        min = 0,
        max = 10000
        )
        
    number_of_frames_to_apply: bpy.props.IntProperty(
        name = "Number of Samples",
        description="Number of Samples to read in and apply",
        default = 10000,
        min = 0,
        max = 10000
        )


    keyframe_every_n_frames: bpy.props.IntProperty(
        name = "Mouth Keyframe Number",
        description="Frame to Apply a Keyframe to, 1 is every frame",
        default = 3,
        min = 1,
        max = 100
        )
    source_rig_name: bpy.props.StringProperty(
        name="Source Rig Name",
        description="Rig Name to Apply Capture To",
        default="",
        maxlen=1024
        )
    destination_rig_name: bpy.props.StringProperty(
        name="Destination Rig Name",
        description="Rig Name to Apply Capture To",
        default="",
        maxlen=1024
        )
    
class KeeMapBoneMappingListItem(bpy.types.PropertyGroup): 
      #"""Group of properties representing a bone mapping from OpenPose to a Rig""" 
      
    name : bpy.props.StringProperty()
    label : bpy.props.StringProperty()
    description : bpy.props.StringProperty()

    SourceBoneName: bpy.props.StringProperty(
        name="Source Bone Name",
        description="This is the name for the rig bone name.",
        default="",
        maxlen=1024
        )

    DestinationBoneName: bpy.props.StringProperty(
        name="Destination Bone Name",
        description="This is the name for the rig bone name.",
        default="",
        maxlen=1024
        )



####################################################################################
####################################################################################
####################################################################################
# Code for iteration through frames and applying positions and angles to rig
####################################################################################
####################################################################################
####################################################################################

class PerformAnimationTransfer(bpy.types.Operator):
    bl_idname = "wm.perform_animation_transfer"
    bl_label = "Read in OpenPose JSON Files and Apply to Character"

    def execute(self, context):
        SourceArmName = "Root"
        DestArmName = "Genesis8Male"
        KeyFrame_Every_Nth_Frame = 3
        NumberOfFramesToTransfer = 20
        #StartFrame = scene.frame_current
        StartFrame = 0


        print('')
        print('Start of Everything')
        print('')
        #SourcArm = bpy.context.selected_objects[SourcArmName]
        #DestArm  = bpy.context.selected_objects[DestArmName]
        SourceArm = bpy.data.objects[SourceArmName]
        DestArm  = bpy.data.objects[DestArmName]
        scene = bpy.context.scene
        keyFrame = True
        #destination_bone =  DestArm.pose.bones["hip"]
        #sourceBone = SourceArm.pose.bones["Hips"]
        #WsPosition = sourceBone.matrix.translation
        #matrix_final = SourceArm.matrix_world @ sourceBone.matrix
        #destination_bone.matrix.translation = matrix_final.translation

        NoCorrection = mathutils.Quaternion((1,0,0,0))
        Correction_p90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(90.0), math.radians(0)), 'XYZ').to_quaternion()
        Correction_n90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(-90.0), math.radians(0)), 'XYZ').to_quaternion()
        Correction_180_X_Quat = mathutils.Euler((math.radians(180), math.radians(0), math.radians(0)), 'XYZ').to_quaternion()
        Correction_270_X_Quat = mathutils.Euler((math.radians(270), math.radians(0), math.radians(0)), 'XYZ').to_quaternion()
        Correction_180_Y_Quat = mathutils.Euler((math.radians(0), math.radians(180), math.radians(0)), 'XYZ').to_quaternion()
        Correction_Stoop_Quat1 = mathutils.Euler((math.radians(-36), math.radians(177), math.radians(3.63)), 'XYZ').to_quaternion()
        Correction_Stoop_Quat = mathutils.Euler((math.radians(-13.5), math.radians(94.9), math.radians(-42.6)), 'XYZ').to_quaternion()
        Correction_p180_Y_Quat = mathutils.Euler((math.radians(0), math.radians(180), math.radians(0)), 'XYZ').to_quaternion()



        i=0
        while (i < NumberOfFramesToTransfer):
            #scene.frame_current = StartFrame + i
            bpy.context.scene.frame_set(StartFrame + i)
            Update()
            
            print('')
            CurrentFrame = scene.frame_current
            EndFrame =  StartFrame + NumberOfFramesToTransfer
            PercentComplete = ((CurrentFrame - StartFrame)/(EndFrame - StartFrame))*100
            print('Working On Frame: ' + str(scene.frame_current) + ' of ' + str(EndFrame) + ' ' + "{:.1f}".format(PercentComplete) + '%')
            print('')
            SetBonePosition(SourceArm, "Hips", DestArm, "hip", "", keyFrame)

            SetBoneRotation(SourceArm, "Hips", DestArm, "hip", "", Correction_270_X_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "Hips", DestArm, "pelvis", "", Correction_270_X_Quat, keyFrame, False)

            SetBoneRotation(SourceArm, "Spine", DestArm, "abdomenLower", "", Correction_Stoop_Quat1, keyFrame, False)
            SetBoneRotation(SourceArm, "Spine1", DestArm, "abdomenUpper", "", Correction_Stoop_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "Spine2", DestArm, "chestLower", "", Correction_Stoop_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "Spine2", DestArm, "chestUpper", "", Correction_Stoop_Quat, keyFrame, False)

            SetBoneRotation(SourceArm, "RightShoulder", DestArm, "rCollar", "", Correction_p90_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "RightArm", DestArm, "rShldrBend", "rShldrTwist", NoCorrection, keyFrame, False)
            SetBoneRotation(SourceArm, "RightForeArm", DestArm, "rForearmBend", "rForearmTwist", NoCorrection, keyFrame, True)

            SetBoneRotation(SourceArm, "LeftShoulder", DestArm, "lCollar", "", Correction_n90_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "LeftArm", DestArm, "lShldrBend", "lShldrTwist", NoCorrection, keyFrame, False)
            SetBoneRotation(SourceArm, "LeftForeArm", DestArm, "lForearmBend", "lForearmTwist", NoCorrection, keyFrame, True)

            SetBoneRotation(SourceArm, "RightUpLeg", DestArm, "rThighBend", "rThighTwist", Correction_180_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "RightLeg", DestArm, "rShin", "", Correction_180_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "RightFoot", DestArm, "rFoot", "", Correction_n90_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "RightFoot", DestArm, "rMetatarsals", "", Correction_n90_Y_Quat, keyFrame, False)
            #    SetBoneRotation(SourceArm, "RightFoot.001", DestArm, "rToe", "", NoCorrection, keyFrame, False)

            SetBoneRotation(SourceArm, "LeftUpLeg", DestArm, "lThighBend", "lThighTwist", Correction_180_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "LeftLeg", DestArm, "lShin", "", Correction_180_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "LeftFoot", DestArm, "lFoot", "", Correction_p90_Y_Quat, keyFrame, False)
            SetBoneRotation(SourceArm, "LeftFoot", DestArm, "lMetatarsals", "", Correction_p90_Y_Quat, keyFrame, False)
            #    SetBoneRotation(SourceArm, "LeftFoot.001", DestArm, "lToe", "", Correction_n90_Y_Quat, keyFrame, False)
            i = i + KeyFrame_Every_Nth_Frame
        
    
class KEEMAP_BONE_UL_List(bpy.types.UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # We could write some code to decide which icon to use here... 
        custom_icon = 'BONE_DATA' 
#        ob = data
#        slot = item
#        ma = slot.material
#        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
#            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
#            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
#            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
#            # Note "data" names should never be translated!
#            layout.label(text="", translate=False, icon_value=custom_icon)
#        # 'GRID' layout type should be as compact as possible (typically a single icon!).
#        elif self.layout_type in {'GRID'}:
#            layout.alignment = 'CENTER'
#            layout.label(text="", icon_value=icon)
        
        # Make sure your code supports all 3 layout types if 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            layout.label(text=item.name, icon = custom_icon) 
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon) 
            
       
class KEEMAP_LIST_OT_NewItem(bpy.types.Operator): 
    """Add a new item to the list.""" 
    bl_idname = "keemap_bone_mapping_list.new_item" 
    bl_label = "Add a new item" 

    def execute(self, context): 
        context.scene.keemap_bone_mapping_list.add() 
        return{'FINISHED'}      
    
class KEEMAP_LIST_OT_DeleteItem(bpy.types.Operator): 
    """Delete the selected item from the list.""" 
    bl_idname = "keemap_bone_mapping_list.delete_item" 
    bl_label = "Deletes an item" 
    
    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        index = context.scene.keemap_bone_mapping_list_index 
        bone_mapping_list.remove(index) 
        index = min(max(0, index - 1), len(bone_mapping_list) - 1) 
        return{'FINISHED'}

class KEEMAP_LIST_OT_MoveItem(bpy.types.Operator): 
    """Move an item in the list.""" 
    bl_idname = "keemap_bone_mapping_list.move_item" 
    bl_label = "Move an item in the list" 
    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),)) 

    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def move_index(self): 
        """ Move index of an item render queue while clamping it. """ 
        scene = bpy.context.scene	
        index = scene.keemap_bone_mapping_list_index 
        list_length = len(bpy.context.scene.keemap_bone_mapping_list) - 1 # (index starts at 0) 
        new_index = index + (-1 if self.direction == 'UP' else 1) 
        index = max(0, min(new_index, list_length)) 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list 
        scene = context.scene	
        index = scene.keemap_bone_mapping_list_index 
        neighbor = index + (-1 if self.direction == 'UP' else 1) 
        bone_mapping_list.move(neighbor, index) 
        self.move_index() 
        return{'FINISHED'}
    
class KeeMapToolsPanel(bpy.types.Panel):
    """Creates a Panel for the KeeMap animation retargetting rig addon"""
    bl_label = "KeeMap"
    bl_idname = "KEEMAP_PT_MAINPANEL"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"    
    bl_category = 'KeeMapRig'
    bl_context = "posemode"   

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene	
        layout.operator("wm.perform_animation_transfer") 
            
                            
class KeemapPanelOne(KeeMapToolsPanel, bpy.types.Panel):
    bl_idname = "KEEMAP_PT_TRANSFERSETTINGS"
    bl_label = "Transfer Settings"

    def draw(self, context):
        layout = self.layout
        KeeMap = bpy.context.scene.keemap_settings 
            
        #layout.label(text="Transfer Settings")
        layout.prop(KeeMap, "start_frame_to_apply")
        layout.prop(KeeMap, "number_of_frames_to_apply")
        layout.prop(KeeMap, "keyframe_every_n_frames")
        layout.prop(KeeMap, "source_rig_name")
        layout.prop(KeeMap, "destination_rig_name")
          
class KeemapPanelTwo(KeeMapToolsPanel, bpy.types.Panel):
    bl_idname = "KEEMAP_BONEMAPPING"
    bl_label = "Bone Mapping"

    def draw(self, context):
        layout = self.layout    
        scene = context.scene	
        KeeMap = bpy.context.scene.keemap_settings            
        row = layout.row()
        row.template_list("KEEMAP_BONE_UL_List", "The_Keemap_List", scene, "keemap_bone_mapping_list", scene,"keemap_bone_mapping_list_index")#, type='COMPACT')#, "index")
        row = layout.row() 
        row.operator('keemap_bone_mapping_list.new_item', text='NEW') 
        row.operator('keemap_bone_mapping_list.delete_item', text='REMOVE') 
        row.operator('keemap_bone_mapping_list.move_item', text='UP').direction = 'UP' 
        row.operator('keemap_bone_mapping_list.move_item', text='DOWN').direction = 'DOWN'
        
        if scene.keemap_bone_mapping_list_index >= 0 and scene.keemap_bone_mapping_list: 
            item = scene.keemap_bone_mapping_list[scene.keemap_bone_mapping_list_index] 
            layout = self.layout    
            row = layout.row() 
            row.label(text="Selected Bone Mapping Parameters")
            box = layout.box()
            box.prop(item, "SourceBoneName") 
            box.prop(item, "DestinationBoneName")
# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------
def register():
    bpy.utils.register_class(PerformAnimationTransfer)
    bpy.utils.register_class(KEEMAP_BONE_UL_List)
    bpy.utils.register_class(KeeMapToolsPanel)
    bpy.utils.register_class(KeemapPanelOne)
    bpy.utils.register_class(KeemapPanelTwo)
    bpy.utils.register_class(KeeMapBoneMappingListItem)
    bpy.utils.register_class(KeeMapSettings)
    bpy.utils.register_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_MoveItem)
    bpy.types.Scene.keemap_bone_mapping_list_index = bpy.props.IntProperty()
    bpy.types.Scene.keemap_bone_mapping_list = bpy.props.CollectionProperty(type = KeeMapBoneMappingListItem) 
    bpy.types.Scene.keemap_settings = bpy.props.PointerProperty(type=KeeMapSettings)

def unregister():
    bpy.utils.unregister_class(PerformAnimationTransfer)
    bpy.utils.unregister_class(KEEMAP_BONE_UL_List)
    bpy.utils.unregister_class(KeeMapSettings)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_MoveItem)
    bpy.utils.unregister_class(KeeMapToolsPanel)
    bpy.utils.unregister_class(KeemapPanelOne)
    bpy.utils.unregister_class(KeemapPanelTwo)
    bpy.utils.unregister_class(KeeMapBoneMappingListItem)
    del bpy.types.Scene.keemap_bone_mapping_list
    del bpy.types.Scene.keemap_bone_mapping_list_index
    del bpy.types.Scene.keemap_settings
    
if __name__ == "__main__":
    register()
