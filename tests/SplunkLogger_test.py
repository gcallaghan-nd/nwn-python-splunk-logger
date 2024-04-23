import logging
import os
from unittest.mock import MagicMock, patch

import pytest
from splunk_logger import SplunkLogger

@pytest.fixture()
def mock_dependencies():
    with patch('splunk_logger.SplunkLogger.client.connect') as mock_connect, \
        patch('splunk_logger.SplunkLogger.logging.Logger.info') as mock_info, \
        patch('splunk_logger.SplunkLogger.logging.Logger.warning') as mock_warning, \
        patch('splunk_logger.SplunkLogger.logging.Logger.error') as mock_error, \
        patch('splunk_logger.SplunkLogger.logging.Logger.critical') as mock_critical, \
        patch('splunk_logger.SplunkLogger.SplunkLogger.LogToSplunk') as mock_LogToSplunk:

        if ('LOCAL_LOG_FILE_PATH' in os.environ):
            os.environ.pop('LOCAL_LOG_FILE_PATH')

        mock_log_levels = MagicMock()
        mock_log_levels.info = mock_info
        mock_log_levels.warning = mock_warning
        mock_log_levels.error = mock_error
        mock_log_levels.critical = mock_critical

        yield mock_log_levels, mock_connect, mock_LogToSplunk

@pytest.fixture()
def mock_splunk():
    with patch('splunk_logger.SplunkLogger.client.connect') as mock_connect, \
        patch('splunk_logger.SplunkLogger.SplunkLogger.WriteToFile') as mock_writeToFile:

        if ('LOCAL_LOG_FILE_PATH' in os.environ):
            os.environ.pop('LOCAL_LOG_FILE_PATH')

        mock_service = MagicMock()
        mock_index = MagicMock("mock_index")
        mock_submit = MagicMock("mock_submit")
        mock_index.submit = mock_submit
        mock_service.indexes.__getitem__.return_value = mock_index

        mock_connect.return_value = mock_service
        yield mock_submit, mock_writeToFile

def test_warning_with_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.warning('test_warning', logToSplunk=True)

    mock_connect.assert_called_once()
    mock_log_levels.warning.assert_called_with('test_warning')
    mock_LogToSplunk.assert_called_with(logging.WARNING, 'test_warning')

def test_warning_no_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.warning('test_warning')

    mock_connect.assert_called_once()
    mock_log_levels.warning.assert_called_with('test_warning')
    mock_LogToSplunk.assert_not_called()

def test_info_with_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.info('test_info', logToSplunk=True)

    mock_connect.assert_called_once()
    mock_log_levels.info.assert_called_with('test_info')
    mock_LogToSplunk.assert_called_with(logging.INFO, 'test_info')

def test_info_no_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.info('test_info')

    mock_connect.assert_called_once()
    mock_log_levels.info.assert_called_with('test_info')
    mock_LogToSplunk.assert_not_called()

def test_error_with_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.error('test_error', logToSplunk=True)

    mock_connect.assert_called_once()
    mock_log_levels.error.assert_called_with('test_error')
    mock_LogToSplunk.assert_called_with(logging.ERROR, 'test_error')

def test_error_no_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.error('test_error')

    mock_connect.assert_called_once()
    mock_log_levels.error.assert_called_with('test_error')
    mock_LogToSplunk.assert_not_called()

def test_critical_with_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.critical('test_critical', logToSplunk=True)

    mock_connect.assert_called_once()
    mock_log_levels.error.assert_called_with('test_critical')
    mock_LogToSplunk.assert_called_with(logging.CRITICAL, 'test_critical')

def test_critical_no_logToSplunk(mock_dependencies):
    mock_log_levels, mock_connect, mock_LogToSplunk = mock_dependencies
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.critical('test_critical')

    mock_connect.assert_called_once()
    mock_log_levels.error.assert_called_with('test_critical')
    mock_LogToSplunk.assert_not_called()

def test_LogToSplunk(mock_splunk):
    mock_submit, _ = mock_splunk

    levels = [{'name': 'INFO', 'value': logging.INFO},
              {'name': 'WARNING', 'value': logging.WARNING},
              {'name': 'ERROR', 'value': logging.ERROR},
              {'name': 'CRITICAL', 'value': logging.CRITICAL}]

    logger = SplunkLogger.SplunkLogger('test_logger')

    for level in levels:
        logger.LogToSplunk(level['value'], 'test_message')
        mock_submit.assert_called_with(f"{level['name']}: test_message")

def test_log_to_file(mock_splunk):
    mock_submit, mock_writeToFile = mock_splunk
    logger = SplunkLogger.SplunkLogger('test_logger')

    os.environ['LOCAL_LOG_FILE_PATH'] = 'test_log_file_path'

    logger.LogToSplunk(logging.INFO, 'test_message')
    mock_submit.assert_not_called()

    mock_writeToFile.assert_called_with('INFO: test_message', 'test_log_file_path')

def test_LogToSplunk_exception(mock_splunk):
    mock_submit, _ = mock_splunk
    mock_submit.side_effect = Exception('test_exception')
    logger = SplunkLogger.SplunkLogger('test_logger')
    logger.error = MagicMock()

    logger.LogToSplunk(logging.INFO, 'test_message')
    mock_submit.assert_called_with('INFO: test_message')
    logger.error.assert_called_with('Failed to log to Splunk: test_exception')

@patch('splunk_logger.SplunkLogger.open')
@patch('splunk_logger.SplunkLogger.client.connect')
def test_write_to_file(_, mock_open):

    mock_file_handler = MagicMock(name="MockFileHandler")

    mock_open.return_value = mock_file_handler

    logger = SplunkLogger.SplunkLogger('test_logger')
    log_file_path = 'test_log_file_path.txt'
    msg = 'test_message'

    logger.WriteToFile(msg, log_file_path)
    mock_open.assert_called_with(log_file_path, 'a')

@patch('splunk_logger.SplunkLogger.open')
@patch('splunk_logger.SplunkLogger.client.connect')
def test_write_to_file_exception(_, mock_open):
    logger = SplunkLogger.SplunkLogger('test_logger')
    log_file_path = 'test_log_file_path.txt'
    msg = 'test_message'

    mock_open.side_effect = Exception('test_exception')

    logger.error = MagicMock()
    logger.WriteToFile(msg, log_file_path)
    logger.error.assert_called_with('Failed to write to log file: test_exception')


def test_create_logger_log_to_file_no_error():
    os.environ['LOCAL_LOG_FILE_PATH'] = 'test_log_file_path'
    logger = SplunkLogger.SplunkLogger('test_logger')
    os.environ.pop('LOCAL_LOG_FILE_PATH')

