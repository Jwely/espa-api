import pika


class ProductionConsumer(object):

    def __init__(self):
        conn_params = pika.ConnectionParameters(port=5671, ssl=True)
        connection = pika.BlockingConnection(conn_params)
        self.channel = connection.channel()

    def _on_message(self, channel, method, header, body):
        print "Message:"
        print "\tchannel: %r" % channel
        print "\tmethod: %r" % method
        print "\theader: %r" % header
        print "\tbody: %r" % body
        channel.basic_ack(method.delivery_tag)

    def consume(self):
        for queue in ('test', 'home'):
            self.channel.queue_declare(queue=queue, durable=True,
                                       exclusive=False, auto_delete=False)
            self.channel.basic_consume(self._on_message, queue=queue)

        self.channel.start_consuming()


class ProductionPublisher(object):

    def __init__(self):
        conn_params = pika.ConnectionParameters(port=5671, ssl=True)
        self.connection = pika.BlockingConnection(conn_params)
        self.pub_properties = pika.BasicProperties(content_type='text/plain',
                                                   delivery_mode=1)

    def publish(self, queue, message):
        # message should be a str, or an iterable
        # in case where sending bulk messages
        channel = self.connection.channel()
        channel.queue_declare(queue=queue,
                              durable=True,
                              exclusive=False,
                              auto_delete=False)
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=message,
                              properties=self.pub_properties)
        channel.close()