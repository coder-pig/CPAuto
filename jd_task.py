# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : jd_task.py
   Author   : CoderPig
   date     : 2022-05-27 17:09 
   Desc     : 
-------------------------------------------------
"""
from airtest.core.android import Android
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import random
import cp_utils
import ocr_utils

temp_save_dir = os.path.join(os.getcwd(), "log")


class Task:
    def __init__(self, to_finish_node=None, task_name=None, logger=None):
        self.to_finish_node = to_finish_node
        self.task_name = task_name
        self.logger = cp_utils.default_logger() if logger is None else logger
        self.po = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

    def start(self):
        self.logger.info("任务【{}】执行开始".format(self.task_name))
        self.doing()
        self.logger.info("任务【{}】执行结束".format(self.task_name))

    def doing(self):
        # 具体要完成的任务
        pass

    def to_finish_position(self):
        sleep(1)
        return (self.to_finish_node[0] + random.randint(10, self.to_finish_node[2] - self.to_finish_node[0]),
                self.to_finish_node[1] + random.randint(10, self.to_finish_node[3] - self.to_finish_node[1]))

    def browser_8s(self):
        task_flag = exists(Template(r"8s_task_flag.png", record_pos=(-0.383, -0.431), resolution=(1080, 2160)))
        if task_flag:
            sleep(10)
            keyevent("KEYCODE_BACK")
        else:
            sleep(20)
            keyevent("KEYCODE_BACK")


class BrowserTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览可得3000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(5)
        keyevent("KEYCODE_BACK")


class SmallAppTask(Task):
    def __init__(self):
        super().__init__(task_name="去参与小程序活动可得8000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(3)
        activity_infos = shell('dumpsys activity top | grep ACTIVITY')
        activity_pos = activity_infos.find("com.jingdong.app.mall")
        if activity_pos == -1:
            start_app("com.jingdong.app.mall")
            sleep(2)


class BrowseAttention8sTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览并关注8s可得8000金币")

    def doing(self):
        touch(self.to_finish_position())
        self.browser_8s()


class Browse8sTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览8s可得7000金币")

    def doing(self):
        touch(self.to_finish_position())
        self.browser_8s()


class Browser4Commodity(Task):
    def __init__(self):
        super().__init__(task_name="累计浏览4个商品可得5000金币")
        # 点我浏览的坐标点
        self.click_pos_tuple = (
            (366, 1115),
            (922, 1117),
            (394, 1822),
            (911, 1872),
        )

    def doing(self):
        touch(self.to_finish_position())
        # 静待片刻等待加载完毕
        sleep(4)
        for click_pos in self.click_pos_tuple:
            # 坐标加上随机数，不然每次点同一个位置，太假了
            touch((click_pos[0] + random.randint(0, 10), click_pos[1] + random.randint(0, 10)))
            sleep(2)
            keyevent("KEYCODE_BACK")
            sleep(2)
        keyevent("KEYCODE_BACK")


class AddOnBrowser4Commodity(Task):
    def __init__(self):
        super().__init__(task_name="累计浏览并加购4个商品可得4000金币")
        # 点我浏览的坐标点
        self.click_pos_tuple = (
            (366, 1115),
            (922, 1117),
            (394, 1822),
            (911, 1872),
        )

    def doing(self):
        touch(self.to_finish_position())
        # 静待片刻等待加载完毕
        sleep(4)
        for click_pos in self.click_pos_tuple:
            # 坐标加上随机数，不然每次点同一个位置，太假了
            touch((click_pos[0] + random.randint(0, 10), click_pos[1] + random.randint(0, 10)))
            sleep(2)
            keyevent("KEYCODE_BACK")
            sleep(3)
        keyevent("KEYCODE_BACK")


class JoinAndBrowser(Task):
    def __init__(self):
        super().__init__(task_name="成功入会并浏览可得3000-8000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(3)
        keyevent("KEYCODE_BACK")


class FocusOnAndBrowserTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览并关注可得3000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(5)
        keyevent("KEYCODE_BACK")


class ZhongCaoTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览可得4000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(5)
        snapshot_path = os.path.join(temp_save_dir, snapshot()['screen'])
        ocr_dict = ocr_utils.picture_local_ocr(snapshot_path)
        # 获取真正喜欢的坐标，跟下一个的Y坐标相差不多
        next_node = ()
        like_node_list = []
        for ocr_key in ocr_dict.keys():
            if "下一个" in ocr_key:
                next_node = ocr_dict[ocr_key]
            elif "喜欢" in ocr_key:
                like_node_list.append(ocr_dict[ocr_key])
        like_node = ()
        for node in like_node_list:
            if abs(next_node[1] - node[1]) < 50:
                like_node = node
                break
        for i in range(0, 4):
            sleep(2)
            touch((int((like_node[0] + like_node[2]) / 2), int(like_node[1] + like_node[3]) / 2))
            sleep(3)
            keyevent("KEYCODE_BACK")
        keyevent("KEYCODE_BACK")


class Browser2000Order10000Task(Task):
    def __init__(self):
        super().__init__(task_name="下单再得10000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(3)
        activity_infos = shell('dumpsys activity top | grep ACTIVITY')
        activity_pos = activity_infos.find("com.jingdong.app.mall")
        if activity_pos == -1:
            start_app("com.jingdong.app.mall")
            sleep(3)
            keyevent("KEYCODE_BACK")


class BrowserBoutiqueShopTask(Task):
    def __init__(self):
        super().__init__(task_name="浏览5个品牌墙店铺可得4000金币")

    def doing(self):
        touch(self.to_finish_position())
        sleep(3)
        snapshot_path = os.path.join(temp_save_dir, snapshot()['screen'])
        ocr_dict = ocr_utils.picture_local_ocr(snapshot_path)
        shop_node_count = 0
        for ocr_key in ocr_dict.keys():
            if shop_node_count < 6 and ocr_dict[ocr_key][1] > int(Android().get_current_resolution()[1] / 2):
                touch((int((ocr_dict[ocr_key][0] + ocr_dict[ocr_key][2]) / 2),
                      int((ocr_dict[ocr_key][1] + ocr_dict[ocr_key][3]) / 2)))
                shop_node_count += 1
                sleep(3)
                keyevent("KEYCODE_BACK")
                sleep(2)
        for i in range(1, 10):
            shell("input swipe 534 1000 534 1400")


class WithdrawalTask(Task):
    def __init__(self):
        super().__init__(task_name="下单返现金")

    def doing(self):
        touch(self.to_finish_position())
        sleep(14)
        withdrawal_click = exists(
            Template(r"withdrawal_click.png", record_pos=(0.007, -0.214), resolution=(1080, 2160)))
        if withdrawal_click:
            touch(withdrawal_click)
        keyevent("KEYCODE_BACK")


class InviteTask(Task):
    def __init__(self):
        super().__init__(task_name="邀请任务")

    def doing(self):
        self.logger.info("邀请任务不做任何操作")
