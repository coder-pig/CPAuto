# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : jd_auto.py
   Author   : CoderPig
   date     : 2022-05-27 17:09 
   Desc     : 
-------------------------------------------------
"""
import re

import cp_file_utils
import ocr_utils
from jd_task import *

# 设备id
device_id = '467fca33'
# 临时图片保存路径
temp_save_dir = os.path.join(os.getcwd(), "log")
# 日志工具初始化
logger = cp_utils.logging_init()
# 匹配任务描述的正则
task_desc_pattern = re.compile(r"可得.*?金", re.S)
# 匹配任务计数器的正则
task_counter_pattern = re.compile(r"(\d)?/(\d)", re.S)
# 识别后干掉数字和、的正则
ocr_replace_index_pattern = re.compile(r"\d+、(.*?)", re.S)
# 二次检查任务是否都完成的标记
no_task_flag = False
# 逛逛并下单的标记
browser_and_order = False


# 一些初始化工作
def init():
    cp_file_utils.is_dir_existed(temp_save_dir, True, True)
    # 连接设备
    auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/{}".format(device_id)])
    logger.info("初始化完成...")


# 初始化任务状态
def task_status():
    global no_task_flag
    logger.info("开始执行任务分析...")
    snapshot_path = os.path.join(temp_save_dir, snapshot()['screen'])
    ocr_dict = ocr_utils.picture_local_ocr(snapshot_path)
    # 任务包装类列表
    task_wrapper_list = []
    # 去完成结点的序号
    to_finish_node_position_list = []
    to_finish_node_list = []
    for index, ocr_key in enumerate(ocr_dict.keys()):
        if "去完成" in ocr_key:
            to_finish_node_position_list.append(index)
            to_finish_node_list.append(ocr_dict[ocr_key])
    # 向前或向后检索任务名称和任务描述
    for index, to_finish_node_position in enumerate(to_finish_node_position_list):
        ocr_dict_keys_list = list(ocr_dict.keys())
        # 初始化任务包装对象
        task_wrapper = TaskWrapper(to_finis_node=to_finish_node_list[index])
        temp_str_list = []
        # 向前检索
        for key in reversed(ocr_dict_keys_list[:to_finish_node_position]):
            if "已完成" in key or "去完成" in key or "去分享" in key or "去领取" in key:
                break
            elif "/" in key:
                temp_str_list.append(key)
        # 向后检索
        for key in ocr_dict_keys_list[to_finish_node_position + 1:]:
            if "已完成" in key or "去完成" in key or "去分享" in key or "去领取" in key or "京东金融" in key or "去微信小程序" in key:
                break
            elif len(key) > 7:
                temp_str_list.append(key)
        # 任务描述与任务名称的一系列判定
        is_fetch_task_counter = False
        task_desc_temp = ""
        for temp_str in temp_str_list:
            task_counter_result = task_counter_pattern.search(temp_str)
            if task_counter_result is not None:
                if not is_fetch_task_counter:
                    task_wrapper.task_name = ocr_replace_index_pattern.sub(r"\g<1>", temp_str).replace(" ", "")
                    task_wrapper.cur_count = task_counter_result.group(1)
                    task_wrapper.sum_count = task_counter_result.group(2)
                    is_fetch_task_counter = True
            else:
                task_desc_temp += temp_str
        # 数字可能存在识别不了的情况，如果为空赋初值
        if task_wrapper.cur_count is None:
            task_wrapper.cur_count = 0
        if task_wrapper.sum_count is None:
            task_wrapper.cur_count = 3
        task_wrapper.task_desc = ocr_replace_index_pattern.sub(r"\g<1>", task_desc_temp).replace(" ", "")
        task_wrapper_list.append(task_wrapper)
    if len(task_wrapper_list) == 0:
        if no_task_flag:
            logger.info("所有任务已完成")
            return
        else:
            logger.info("未检测到有可完成任务，进行二次校验")
            no_task_flag = True
            task_status()
            return
    # 如果只剩下一个任务，且为下单得10000，说明所有任务已完成
    elif len(task_wrapper_list) == 1 and browser_and_order:
        logger.info("所有任务已完成")
        return
    logger.info("任务分析完毕，开始执行任务...")
    for wrapper in task_wrapper_list:
        wrapper.show()
        task_list = wrapper.generate_task_list()
        for task in task_list:
            sleep(3)
            task.start()
    task_status()


# 任务包装类
class TaskWrapper:
    def __init__(self, to_finis_node=None, task_name=None, task_desc=None, cur_count=0, sum_count=0):
        self.to_finis_node = to_finis_node
        self.task_name = task_name
        self.task_desc = task_desc
        self.cur_count = cur_count
        self.sum_count = sum_count

    # 生成任务列表
    def generate_task_list(self):
        task_type = self.decision_task()
        task_list = []
        if task_type is not None:
            task_count = int(self.sum_count) - int(self.cur_count)
            for i in range(0, task_count):
                task = eval(task_type)
                task.to_finish_node = self.to_finis_node
                task_list.append(task)
        return task_list

    # 任务判定(匹配多个关键词)
    def decision_task(self):
        global browser_and_order
        if len(self.task_desc) != 0:
            if self.have_all_sub_string(['浏览', "关注", "8s", "8000"]):
                return 'BrowseAttention8sTask()'
            elif self.have_all_sub_string(['浏览', "4000"]):
                return 'ZhongCaoTask()'
            elif self.have_all_sub_string(['浏览', "8s", "7000"]):
                return 'Browse8sTask()'
            elif self.have_all_sub_string(['浏览', "4个", "5000"]):
                self.sum_count = 1
                return 'Browser4Commodity()'
            elif self.have_all_sub_string(['览', "加购", "4个", "4000"]):
                self.sum_count = 1
                return 'AddOnBrowser4Commodity()'
            elif self.have_all_sub_string(['入会', "浏览", "3000"]):
                return 'JoinAndBrowser()'
            elif self.have_all_sub_string(['浏览', "关注", "3000"]):
                return 'FocusOnAndBrowserTask()'
            elif self.have_all_sub_string(['浏览', "3000"]):
                return 'BrowserTask()'
            elif self.have_all_sub_string(['下单', "2000", "10000"]):
                if not browser_and_order:
                    browser_and_order = True
                    return 'Browser2000Order10000Task()'
                else:
                    return None
            elif self.have_all_sub_string(['小程序', "8000"]):
                return 'SmallAppTask()'
            elif self.have_all_sub_string(['下单', "返现", "提现"]):
                return 'WithdrawalTask()'
        else:
            # 去加购任务描述有时会识别不到
            if "去加购" in self.task_name:
                self.sum_count = 1
                return 'AddOnBrowser4Commodity()'
            elif "去逛逛" in self.task_name:
                if not browser_and_order:
                    browser_and_order = True
                    return 'Browser2000Order10000Task()'
                else:
                    return None
            else:
                logger.info("存在无法识别的任务，请检查后重试！{}".format(self.show()))

    def have_all_sub_string(self, match_str_list):
        for match_str in match_str_list:
            if match_str not in self.task_desc:
                return False
        return True

    def show(self):
        logger.info(
            "{} → 【{}】→【{}】→【{}/{}】".format(self.to_finis_node, self.task_name, self.task_desc, self.cur_count,
                                            self.sum_count))


if __name__ == '__main__':
    init()
    task_status()
