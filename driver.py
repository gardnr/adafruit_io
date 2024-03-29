import time

from Adafruit_IO import Client, Feed, RequestError, ThrottlingError

from gardnr import constants, drivers, logger


class AdafruitIO(drivers.Exporter):

    THROTTLE_SLEEP_TIME = 60

    blacklist = [constants.IMAGE, constants.NOTES]

    username = 'IO_USER'
    key = 'IO_KEY'


    def setup(self):
        self.client = Client(self.username, self.key)
        self.feed_cache = {}


    def get_feed(self, metric_name):

        # make request for feed if it hasn't been retrieved yet
        if metric_name not in self.feed_cache:
            try:
                feed = self.client.feeds(metric_name)
            except RequestError: # Doesn't exist, create a new feed
                feed = self.client.create_feed(Feed(name=metric_name))

            self.feed_cache[metric_name] = feed

        return self.feed_cache[metric_name]


    def export(self, logs):

        # TODO: user send_batch_data instead
        # https://github.com/adafruit/Adafruit_IO_Python/blob/869cf3547cbda48a3e51029419cf82cef4c5b8ad/Adafruit_IO/client.py#L158

        for log in logs:
            feed = self.get_feed(log.metric.name)

            try:
                self.client.send_data(feed.key, log.value, {'created_at': log.timestamp.isoformat(), 'lat': '0', 'lon': '0', 'ele': '0'})
            except ThrottlingError:
                logger.warning('Adafruit max requests reached, sleeping...')
                time.sleep(self.THROTTLE_SLEEP_TIME)
                logger.warning('Sleep done, attempting request again')
                self.client.send_data(feed.key, log.value, {'created_at': log.timestamp.isoformat(), 'lat': '0', 'lon': '0', 'ele': '0'})
