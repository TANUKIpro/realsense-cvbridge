#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import os
import time
import cv2
import sys
import numpy as np
import message_filters
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

class depth_reader:
    def __init__(self):
        rospy.init_node('depth_reader', anonymous=True)
        self.bridge = CvBridge()
        #適当なTopicを選択し、サブスクライバを定義
        sub_rgb = message_filters.Subscriber("/camera/color/image_raw",Image)
        sub_depth = message_filters.Subscriber("camera/depth/image_rect_raw",Image)
        #RGBとdepthを補正
        self.mf = message_filters.ApproximateTimeSynchronizer([sub_rgb, sub_depth], 100, 10.0)
        self.mf.registerCallback(self.ImageCallback)
        #マウスイベントの設定
        self.input_img_name="color_image"
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None}

    #ここからマウス関係のプログラム
    def __CallBackFunc(self, eventType, x, y, flags, userdata):
        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType    
        self.mouseEvent["flags"] = flags

    def getData(self):
        return self.mouseEvent
        
    def getEvent(self):
        return self.mouseEvent["event"]                

    def getFlags(self):
        return self.mouseEvent["flags"]                

    def posXY(self):
        x = self.mouseEvent["x"]
        y = self.mouseEvent["y"]
        return (x, y)

    def draw(self, image, width, height, depth):
        #画像に赤の十字を描画
        cv2.line(image, ((width/2)-15, height/2), ((width/2)+15, height/2), (0, 0, 255), 2)
        cv2.line(image, (width/2, (height/2)-15), (width/2, (height/2)+15), (0, 0, 255), 2)
        #width, height, depth情報を表示
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image,"width={0}, height={1}".format(width, height) , (10,15), font, .5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image,"+:depth={0}".format(depth) , (10,30), font, .5, (0,0,0), 1, cv2.LINE_AA)

    def ImageCallback(self, rgb_data , depth_data):
        try:
            color_image = self.bridge.imgmsg_to_cv2(rgb_data, 'passthrough')
            depth_image = self.bridge.imgmsg_to_cv2(depth_data, 'passthrough')
        except CvBridgeError, e:
            rospy.logerr(e)

        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        h, w, c = color_image.shape
        dc_info = depth_image[h/2][w/2]
        self.draw(color_image, w, h, dc_info)
        
        cv2.namedWindow("color_image")
        #マウスのコールバック
        cv2.setMouseCallback(self.input_img_name, self.__CallBackFunc)
        cv2.imshow("color_image", color_image)
        #rospy.loginfo(d_info)
        #ここらでマウスの座標とdepth情報を対応
        m_x, m_y = self.posXY()
        d_info = depth_image[m_y][m_x]
        if self.getEvent() == cv2.EVENT_LBUTTONDOWN:
            print("clicked point is [X:{0}, Y:{1}], depth info is [{2}]"
                    .format(m_x, m_y, d_info))
            rospy.loginfo("clicked L-button")
        cv2.waitKey(20)
        
        
        
if __name__ == '__main__':
    try:
        de = depth_reader()
        rospy.spin()
    except rospy.ROSInterruptException: pass
    
    
