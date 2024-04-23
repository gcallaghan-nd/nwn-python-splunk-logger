import logging
import datetime
import os
from splunklib import client

class SplunkLogger(logging.Logger):

    def __init__(self, name, level = logging.NOTSET):
        logging.Logger.__init__(self, name, level)
        log_file_path = os.environ.get('LOCAL_LOG_FILE_PATH')
        if (not log_file_path):
            service = client.connect(host='localhost', port=8089, username='admin', password='changeme')
            self.index = service.indexes[os.environ.get('SPLUNK_INDEX')]
        return super(SplunkLogger, self).__init__(name, level)

    def warning(self, msg, logToSplunk = False, *args, **kwargs):
        if logToSplunk:
            self.LogToSplunk(logging.WARNING, msg)
        return super(SplunkLogger, self).warning(msg, *args, **kwargs)

    def info(self, msg, logToSplunk = False, *args, **kwargs):
        if logToSplunk:
            self.LogToSplunk(logging.INFO, msg)
        return super(SplunkLogger, self).info(msg, *args, **kwargs)

    def error(self, msg, logToSplunk = False, *args, **kwargs):
        if logToSplunk:
            self.LogToSplunk(logging.ERROR, msg)
        return super(SplunkLogger, self).error(msg, *args, **kwargs)

    def critical(self, msg, logToSplunk = False, *args, **kwargs):
        if logToSplunk:
            self.LogToSplunk(logging.CRITICAL, msg)
        return super(SplunkLogger, self).error(msg, *args, **kwargs)

    def LogToSplunk(self, level, msg):
        try:
            levelName = logging.getLevelName(level)
            print(f"Log {levelName} to Splunk: {msg}")
            msg = f"{levelName}: {msg}"

            log_file_path = os.environ.get('LOCAL_LOG_FILE_PATH')
            if (log_file_path):
                self.WriteToFile(msg, log_file_path)
                return

            self.index.submit(msg)
        except Exception as e:
            self.error(f"Failed to log to Splunk: {e}")

    def WriteToFile(self, msg, log_file_path):
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"{current_time}: {msg}"

            with open(log_file_path, 'a') as f:
                f.write(msg + '\n')
        except Exception as e:
            self.error(f"Failed to write to log file: {e}")

logging.setLoggerClass(SplunkLogger)
logging.basicConfig()