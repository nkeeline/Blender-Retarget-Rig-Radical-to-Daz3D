import bpy
import math
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
    
    #rotate the edit rotation quat first to armature rotation
    #ArmatureSpaceBoneEditPosition = RigArmature.rotation_quaternion * BoneEditRotation
    if(DestinationTwistBoneName != ""):
        TwistBone = DestinationArmature.pose.bones[DestinationTwistBoneName]
    destination_bone =  DestinationArmature.pose.bones[DestinationBoneName]
    sourceBone = SourceArmature.pose.bones[SourceBoneName]
    
    #Set Bone Position now that we've calculated it.
    destination_bone.rotation_mode = 'QUATERNION'
     
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
    
    #get the source bones rotation in world space.
    dest_bone_world_matrix = dest_arm_matrix @ dest_bone_matrix
    
    DestBoneRotWS = dest_bone_world_matrix.to_quaternion()
    #print('Destination Rotation')
    #print(DestBoneRotWS)
    
    DifferenceBetweenSourceWSandDestWS = DestBoneRotWS.rotation_difference(SourceBoneRotWS)
    #print('Difference Rotation')
    #print(DifferenceBetweenSourceWSandDestWS)
    
    destination_bone.rotation_quaternion = destination_bone.rotation_quaternion @ DifferenceBetweenSourceWSandDestWS @ CorrectionQuat
    
    
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

SourceArmName = "Reference"
DestArmName = "Leopold"
KeyFrame_Every_Nth_Frame = 3
NumberOfFramesToTransfer = 150


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
Correction_180_Y_Quat = mathutils.Euler((math.radians(0), math.radians(180), math.radians(0)), 'XYZ').to_quaternion()
Correction_Stoop_Quat = mathutils.Euler((math.radians(22), math.radians(0.0), math.radians(0)), 'XYZ').to_quaternion()
Correction_p180_Y_Quat = mathutils.Euler((math.radians(0), math.radians(180), math.radians(0)), 'XYZ').to_quaternion()



StartFrame = scene.frame_current
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

    SetBoneRotation(SourceArm, "Hips", DestArm, "hip", "", Correction_180_X_Quat, keyFrame, False)
    SetBoneRotation(SourceArm, "Hips", DestArm, "pelvis", "", Correction_180_X_Quat, keyFrame, False)

    SetBoneRotation(SourceArm, "Spine", DestArm, "abdomenLower", "", Correction_Stoop_Quat, keyFrame, False)
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
    SetBoneRotation(SourceArm, "RightFoot.001", DestArm, "rToe", "", NoCorrection, keyFrame, False)

    SetBoneRotation(SourceArm, "LeftUpLeg", DestArm, "lThighBend", "lThighTwist", Correction_180_Y_Quat, keyFrame, False)
    SetBoneRotation(SourceArm, "LeftLeg", DestArm, "lShin", "", Correction_180_Y_Quat, keyFrame, False)
    SetBoneRotation(SourceArm, "LeftFoot", DestArm, "lFoot", "", Correction_p90_Y_Quat, keyFrame, False)
    SetBoneRotation(SourceArm, "LeftFoot", DestArm, "lMetatarsals", "", Correction_p90_Y_Quat, keyFrame, False)
    SetBoneRotation(SourceArm, "LeftFoot.001", DestArm, "lToe", "", Correction_n90_Y_Quat, keyFrame, False)
    i = i + KeyFrame_Every_Nth_Frame
