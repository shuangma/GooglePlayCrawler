#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess


class Command:
    def __init__(self):
        pass

    @staticmethod
    def run(cmd, shell=False, input_data=None):
        proc = subprocess.Popen(cmd,
                                shell=shell,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        output, error = proc.communicate(input=input_data)

        proc.wait()

        return output, error

    @staticmethod
    def run_without_wait(cmd, shell=False):
        proc = subprocess.Popen(cmd,
                         shell=shell,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)


        # output, error = proc.communicate()
        # print output, error

