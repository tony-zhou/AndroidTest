#!/usr/bin/env python3
# coding=utf-8
import os
import time
import shutil
import subprocess


__author__ = 'tony'


class Common(object):

    @staticmethod
    def gen_devices_id(single=False):
        if not Common.check_connection():
            Common.print_log('there is no connected device')
            exit()
        Common.print_log("start to get devices id")
        total_devices_id = []
        valid = False
        while not valid:
            devices_info = Common.adb('devices')[0].split('\n')
            for detail_info in devices_info[::-1]:
                if '' == detail_info or 'List' in detail_info:
                    continue
                else:
                    if 'offline' in detail_info:
                        Common.print_log(''.join(["device ", detail_info.split('\t')[0], "offline"]))
                        input("please press Enter to retry after check")
                        valid = False
                        break
                    elif 'unauthorized' in detail_info:
                        Common.print_log(''.join(["device", detail_info.split('\t')[0], "unauthorized"]))
                        input("please press Enter to retry after check")
                        valid = False
                        break
                    elif 'device' in detail_info:
                        total_devices_id.append(detail_info.split('\t')[0])
                        valid = True
        devices_number = len(total_devices_id)
        if single and devices_number > 1:
            Common.print_log('there are multi devices connected')
            exit()
        else:
            return total_devices_id

    @staticmethod
    def gen_device_info(device_id):
        Common.print_log('start to get device info', device_id)
        info = Common.command('adb -s %s shell getprop' % device_id)
        device_info = info[0].strip()
        brand_pattern = "\[ro.product.brand\].*?\[(.*?)\]"
        model_pattern = "\[ro.product.model\].*?\[(.*?)\]"
        brand = re.findall(brand_pattern, device_info)[0]
        model = re.findall(model_pattern, device_info)[0]
        if not bool(model):
            model = device_id
        return brand.upper(), model.upper()

    @staticmethod
    def check_connection(device_id=""):
        if bool(device_id):
            devices_info = Common.adb('get-state', device_id)[0]
            a = type(devices_info)
            if 'device' in devices_info:
                return True
            else:
                return False
        else:
            devices_info = Common.adb('devices')[0].split()
            if 'device' in devices_info:
                return True
            else:
                return False

    @staticmethod
    def confirm_connection(device_id):
        valid = False
        while not valid:
            time.sleep(1)
            devices_info = Common.adb('devices')[0].split('\n')
            for check_valid in devices_info[::-1]:
                if device_id in check_valid and 'device' in check_valid:
                    valid = True
                    break
            if not valid:
                input(u"device {0:s} is invalid, press Enter after check to retry".format(device_id))
        return True

    @staticmethod
    def adb(cmd, device_id=''):
        cmd = u"adb -s {0:s} {1:s}".format(device_id, cmd) if bool(device_id) else u"adb {0:s}".format(cmd)
        f = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        feedback = f.communicate()
        return feedback

    @staticmethod
    def adb_shell(cmd, device_id=''):
        cmd = u"adb -s {0:s} shell {1:s}".format(device_id, cmd) if bool(device_id) else u"adb shell {0:s}".format(cmd)
        f = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        feedback = f.communicate()
        return feedback

    @staticmethod
    def command(cmd):
        f = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        feedback = f.communicate()
        return feedback

    @staticmethod
    def print_log(info, tag=''):
        time_stamp = time.strftime(r'%Y-%m-%d %H:%M:%S', time.localtime())
        if bool(tag):
            print(''.join([time_stamp, ' '*8, tag, ' '*8, info]))
        else:
            print(''.join([time_stamp, ' '*8, info]))

    @staticmethod
    def save_log(log, info, tag):
        with open(log, 'a+', encoding='utf-8') as file:
            time_stamp = time.strftime(r'%Y-%m-%d %H:%M:%S', time.localtime())
            if bool(tag):
                file.write(''.join([time_stamp, ' '*8, tag, ' '*8, info]))
            else:
                file.write(''.join([time_stamp, ' '*8, info]))
            file.close()

    @staticmethod
    def confirm_path(path, update=False):
        if os.path.exists(path):
            if update:
                try:
                    shutil.rmtree(path)
                except IOError:
                    Common.print_log('delete files in {0:s} fail, please close it and retry'.format(path))
                    exit()
        else:
            if os.path.exists(os.path.basename(path)):
                os.mkdir(path)
            else:
                os.makedirs(path)


if __name__ == "__main__":
    pass
