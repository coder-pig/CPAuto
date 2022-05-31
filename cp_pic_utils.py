# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : cp_pic_utils.py
   Author   : CoderPig
   date     : 2022-05-23 16:09 
   Desc     : 图片相关工具类
-------------------------------------------------
"""
import cv2
import numpy as np
from PIL import Image
from airtest.core.api import *

import cp_utils
import cp_file_utils

# 均值哈希算法
from task_desc_crop import cal_task_desc_area


def average_hash(img, shape=(10, 10)):
    # 缩放为10*10
    img = cv2.resize(img, shape)
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    hash_str = ''
    # 遍历累加求像素和
    for i in range(shape[0]):
        for j in range(shape[1]):
            s = s + gray[i, j]

    # 求平均灰度
    avg = s / 100
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(shape[0]):
        for j in range(shape[1]):
            if gray[i, j] > avg:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 差值哈希算法
def difference_hash(img, shape=(10, 10)):
    # 缩放10*11
    img = cv2.resize(img, (shape[0] + 1, shape[1]))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(shape[0]):
        for j in range(shape[1]):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 感知哈希算法
def perception_hash(img):
    # 缩放32*32
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:10, 0:10]
    _hash = []
    average = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > average:
                _hash.append(1)
            else:
                _hash.append(0)
    return _hash


# hash值对比
def cmp_hash(hash1, hash2, shape=(10, 10)):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 相等则n计数+1，n最终为相似度
        if hash1[i] == hash2[i]:
            n = n + 1
    return n / (shape[0] * shape[1])


# 单通道直方图算法
def single_channel_calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


# 三通道直方图算法
def three_channel_calculate(image1, image2, size=(256, 256)):
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += single_channel_calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


# 均值哈希算法比较图片相似度
def pic_similar_percent(pic1, pic2):
    img1 = cv2.imread(pic1)
    img2 = cv2.imread(pic2)
    return cmp_hash(average_hash(img1), average_hash(img2))


def pic_perception_percent(pic1, pic2):
    img1 = cv2.imread(pic1)
    img2 = cv2.imread(pic2)
    return cmp_hash(perception_hash(img1), perception_hash(img2))


# 测试函数
def test_pic_match():
    # 暂存目录
    temp_save_dir = os.path.join(os.getcwd(), "temp")
    cp_file_utils.is_dir_existed(temp_save_dir)
    # 生成截图
    snapshot_path = os.path.join(temp_save_dir, str(round(time.time() * 1000)) + ".jpg")
    temp = snapshot(filename=snapshot_path)['screen']
    img = Image.open(snapshot_path)
    task_desc_crop_path_list = []
    for task_desc in cal_task_desc_area():
        region = img.crop(task_desc)
        save_path = os.path.join(temp_save_dir, "crop_" + str(round(time.time() * 1000))) + ".jpg"
        region.save(save_path)
        task_desc_crop_path_list.append(save_path)
    img.close()
    logger.info("截图裁剪完毕，开始进行比对...")
    default_save_dir = os.path.join(os.getcwd(), "default")
    origin_default_img_list = []
    for i in range(1, 6):
        pic_path = os.path.join(default_save_dir, "t{0}.jpg".format(i))
        origin_default_img_list.append(cv2.imread(pic_path))
    for task_desc_crop_path in task_desc_crop_path_list:
        img_temp = cv2.imread(task_desc_crop_path)
        for index, img in enumerate(origin_default_img_list):
            percent = cmp_hash(average_hash(img_temp), average_hash(img))
            if percent > 0.8:
                logger.info("均值哈希算法命中 t{0}.jpg，匹配相似度：{1}".format(index + 1, percent))
            percent = cmp_hash(difference_hash(img_temp), difference_hash(img))
            if percent > 0.8:
                logger.info("差值哈希算法命中 t{0}.jpg，匹配相似度：{1}".format(index + 1, percent))
            percent = cmp_hash(perception_hash(img_temp), perception_hash(img))
            if percent > 0.8:
                logger.info("感知哈希算法命中 t{0}.jpg，匹配相似度：{1}".format(index + 1, percent))
            percent = single_channel_calculate(img_temp, img)
            if percent > 0.8:
                logger.info("单通道直方图算法命中 t{0}.jpg，匹配相似度：{1}".format(index + 1, percent))
            percent = three_channel_calculate(img_temp, img)
            if percent > 0.8:
                logger.info("三通道直方图算法命中 t{0}.jpg，匹配相似度：{1}".format(index + 1, percent))

        # print("均值哈希算法，匹配相似度：")
        # for index, img in enumerate(origin_default_img_list):
        #     print("{0} = t{1}.jpg：{2}".format(task_desc_crop_path, index + 1,
        #                                       cmp_hash(average_hash(img_temp), average_hash(img))))
        # print("差值值哈希算法，匹配相似度：")
        # for index, img in enumerate(origin_default_img_list):
        #     print("{0} = t{1}.jpg：{2}".format(task_desc_crop_path, index + 1,
        #                                       cmp_hash(difference_hash(img_temp), difference_hash(img))))
        # print("感知哈希算法，匹配相似度：")
        # for index, img in enumerate(origin_default_img_list):
        #     print("{0} = t{1}.jpg：{2}".format(task_desc_crop_path, index + 1,
        #                                       cmp_hash(perception_hash(img_temp), perception_hash(img))))
        # print("单通道直方图算法，匹配相似度：")
        # for index, img in enumerate(origin_default_img_list):
        #     print("{0} = t{1}.jpg：{2}".format(task_desc_crop_path, index + 1,
        #                                       single_channel_calculate(img_temp, img)))
        # print("三通道直方图算法，匹配相似度：")
        # for index, img in enumerate(origin_default_img_list):
        #     print("{0} = t{1}.jpg：{2}".format(task_desc_crop_path, index + 1,
        #                                       three_channel_calculate(img_temp, img)))


if __name__ == '__main__':
    logger = cp_utils.logging_init()
    auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/467fca33"])
    logger.info("设备连接成功...")
    test_pic_match()
