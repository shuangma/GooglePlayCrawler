#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika
import os

from common.config import AppConfig
from common.command import Command


class RabbitTopic:
    def __init__(self, exchange_name):
        self._exchange_name = exchange_name

        self.connection = None
        self.channel = None

    def construct_producer(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self._exchange_name, type='topic')

    def publish(self, routing_key, message):
        self.channel.basic_publish(exchange=self._exchange_name, routing_key=routing_key,
                                   body=message)

    def construct_consumer(self, queue_name, max_queue_length, binding_keys):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self._exchange_name, type='topic')

        self.channel.queue_declare(queue=queue_name, arguments={'x-max-length': max_queue_length})

        for binding_key in binding_keys:
            self.channel.queue_bind(exchange=self._exchange_name, queue=queue_name,
                                    routing_key=binding_key)

    def start_consuming(self, callback, queue_name):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(callback, queue=queue_name)
        self.channel.start_consuming()

    @staticmethod
    def init_rabbitmq_producer(exchange_name, logger):
        try:
            rabbit_topic = RabbitTopic(exchange_name)
            rabbit_topic.construct_producer()
        except Exception:
            logger.exception('Construct rabbitmq producer error')
            return None
        return rabbit_topic

    @staticmethod
    def init_rabbitmq_consumer(exchange_name, queue_name, queue_limit, routing_keys, logger):
        try:
            rabbit_topic = RabbitTopic(exchange_name)
            rabbit_topic.construct_consumer(queue_name, queue_limit, routing_keys)
        except Exception:
            logger.exception('Construct category consumer error')
            return None
        return rabbit_topic

    @staticmethod
    def is_queue_full(queue_name, max_length, logger):
        rabbitmq_admin = AppConfig.get_rabbitmq_admin()
        if not os.path.isfile(rabbitmq_admin):
            logger.debug('Rabbitmq admin tool %s not exists' % rabbitmq_admin)
            return False
        cmd = [rabbitmq_admin, 'list', 'queues']
        try:
            output, error = Command.run(cmd)
            if error:
                logger.debug('Run rabbitmq cmd error %s' % error)
            else:
                lines = output.splitlines()
                for line in lines:
                    if queue_name in line:
                        items = line.split('|')
                        if len(items) == 4:
                            queue_num = items[2].strip()
                            queue_num = int(queue_num)
                            logger.info('Queue %s current number: %d' % (queue_name, queue_num))
                            if queue_num >= max_length:
                                return True
        except Exception:
            logger.exception('Rabbitmq cmd "%s" run exception' % ' '.join(cmd))
        return False
