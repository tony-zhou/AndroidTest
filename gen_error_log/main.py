#!/usr/bin/env python3
# coding=utf-8
import os
import time
from utils.commonfun import Common


__author__ = 'tony'


class Remedy(object):

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.error_type = ["data_app_anr", "data_app_crash"]
        self.device_id = Common.gen_devices_id(single=True)[0]

    def get_log(self):
        """
        Main method for dump log
        :return: None
        """
        device_info = '_'.join(Common.gen_device_info(self.device_id)).replace(' ', '_')
        log_path = os.path.join(self.path, *['Log', device_info])
        for item in self.error_type:
            error_list = self.gen_error_list(item)
            Common.print_log("start to get %s log" % item.split('_')[2])
            if bool(error_list):
                item_path = os.path.join(log_path, ''.join(['Log_', item.split('_')[2]]))
                latest_path = os.path.join(item_path, 'Latest')
                Common.confirm_path(item_path, update=False)
                Common.confirm_path(latest_path, update=True)
                self.write_log(latest_path, error_list[0])
                if self.need_to_dump_log(error_list[0]):
                    self.dump_log(latest_path, error_list[0], item)
                if len(error_list) > 1:
                    for e in error_list[1:]:
                        self.write_log(item_path, e)
                print(u"{0:s} logs are successfully exported !".format(
                    ''.join([item.split('_')[2][0].upper(), item.split('_')[2][1:].lower()])))
            else:
                Common.print_log("there is no valid %s log !" % item.split('_')[2])

    def write_log(self, path, error):
        """
        Use "dumpsys dropbox --print" to write error log to file
        :param path: log path
        :param error: error timestamp
        :return: None
        """
        file_name = error.replace(':', '-').replace(' ', '_')
        log_file = os.path.join(path, ''.join([file_name, '.txt']))
        if not os.path.exists(log_file):
            with open(log_file, mode='w', encoding='utf-8') as file:
                cmd = u'dumpsys dropbox --print {0:s}'.format(error)
                log_info = Common.adb_shell(self.device_id, cmd)
                file.write(log_info[0])
                file.close()

    def dump_log(self, path, error, item):
        """
        Dump logcat buffer to local file and if error type is anr, copy traces.txt to local path
        :param path: log path
        :param error: error timestamp
        :param item: error type
        :return: None
        """
        file_name = ''.join([error.replace(':', '-').replace(' ', '_'), 'logcat.txt'])
        log_file = os.path.join(path, file_name)
        if not os.path.exists(log_file):
            with open(log_file, mode='w', encoding='utf-8') as file:
                cmd = 'logcat -v time -d'
                log_info = Common.adb(cmd, self.device_id)
                file.write(log_info[0])
                file.close()
            if item.split('_')[2] == 'anr':
                cmd = u'pull {0:s} {1:s}'.format('/data/anr/traces.txt', path)
                Common.adb(self.device_id, cmd)

    def gen_error_list(self, error_type):
        """
        Get error timestamp list according to the error type
        :param error_type: 'data_app_anr' or 'data_app_crash'
        :return: error list as ['2015-11-24 09:59:38']
        """
        error_list = []
        cmd = 'dumpsys dropbox'
        response = Common.adb_shell(cmd, self.device_id)[0]
        if not bool(response):
            return False
        else:
            result = [x for x in response.strip().split('\n') if error_type in x]
            if result == ['']:
                return False
            else:
                for item in result:
                    if 'contents lost' not in item:
                        time_stamp = ' '.join([item.split(" ")[0], item.split(" ")[1]])
                        error_list.append(time_stamp)
            error_list.sort(reverse=True)
            return error_list

    def need_to_dump_log(self, time_stamp):
        """
        Compare mobile time when issue happened with PC current local time.
        If the time gap are less than 180s, return True, else False.
        :param time_stamp: mobile time when issue happened
        :return: True or False
        """
        log_unix_time = int(time.mktime(time.strptime(time_stamp, '%Y-%m-%d %H:%M:%S')))
        cmd = 'date +%s'
        current_unix_time = Common.adb_shell(cmd, self.device_id)
        current_unix_time = int(current_unix_time[0])
        if (current_unix_time - log_unix_time) in range(180):
            return True
        else:
            return False


if __name__ == "__main__":
    log = Remedy()
    log.get_log()
