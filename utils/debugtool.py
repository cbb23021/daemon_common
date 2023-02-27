import logging
import os
import sys
import threading
import time
import traceback
from flask import request
from logging.handlers import TimedRotatingFileHandler


class _RouteFilter(logging.Filter):
    _msg_list = [
        '/probe'
    ]

    def _check_message(self, _str):
        for msg in self._msg_list:
            if msg in _str:
                return False
        return True

    def filter(self, record):
        _str = record.getMessage()
        return self._check_message(_str=_str)

    def filter_by_loguru(self, record):
        return self._check_message(_str=record)


class _FluentLogger:
    """
        remote logger system
    """

    _SYSTEM_NAME = os.environ.get('SYSTEM_NAME', 'default_log')
    _ENVIRONMENT = os.environ.get('ENVIRONMENT', 'develop')
    _HOST = os.environ.get('FLUENT_CLIENT_HOST', 'fluentd_client')
    _PORT = int(os.environ.get('FLUENT_CLIENT_PORT', 24226))

    @classmethod
    def get_handler(cls, entry_point, level=logging.DEBUG):
        """
            connect local buffer
        """
        from fluent import handler
        import msgpack
        from io import BytesIO

        def overflow_handler(pending):
            unpacker = msgpack.Unpacker(BytesIO(pending))
            for unpacked in unpacker:
                print(f'****** Remote Failed ****** {unpacked}')

        custom_format = {
            'host': '%(hostname)s',
            'where': '%(module)s.%(funcName)s',
            'local_time': '%(asctime)s',
            'type': '%(levelname)s',
            'stack_trace': '%(exc_text)s',
            'entry_point': entry_point,
            'system_name': cls._SYSTEM_NAME
        }
        console = handler.FluentHandler(
            tag=cls._ENVIRONMENT,
            host=cls._HOST,
            port=cls._PORT,
            buffer_overflow_handler=overflow_handler
        )
        console.setLevel(level)
        formatter = handler.FluentRecordFormatter(custom_format)
        console.setFormatter(formatter)
        console.addFilter(_RouteFilter())
        return console


class _LoguruLogger:
    """
        use package "loguru" logging
    """

    _SUB_PATH = 'loguru'
    _TITLE = os.environ.get('SYSTEM_NAME', 'default_log')
    _ABS_PATH = os.path.abspath('.')
    _METHODS = {
        'debug': [f'/log/{_SUB_PATH}/debug_log/', logging.DEBUG],
        'warning': [f'/log/{_SUB_PATH}/warning_log/', logging.WARNING],
        'error': [f'/log/{_SUB_PATH}/error_log/', logging.ERROR],
        'critical': [f'/log/{_SUB_PATH}/critical_log/', logging.CRITICAL]
    }

    @classmethod
    def _init_file_path(cls):
        for key, value in cls._METHODS.items():
            path = value[0]
            os.makedirs(f'{cls._ABS_PATH}{path}', exist_ok=True)

    @classmethod
    def _split_msg(cls, origin_msg):
        """
            轉換msg結構，因為loguru會自動把traceback加到最後面

            f'<MESSAGE>: {msg} | <EXCEPTION>: {exception} | <TRACEBACK>: \n{traceback_result}' ->

            f'<MESSAGE>: {msg} | <EXCEPTION>: {exception}'
        """
        return ' | '.join(origin_msg.split(' | ')[:-1])

    @classmethod
    def _add_file_logger(cls, console, entry_point):
        for key, (path, level) in cls._METHODS.items():
            file_name = f'{cls._ABS_PATH}{path}{cls._TITLE}.{entry_point}.{key}.log'
            console.add(
                file_name,
                level=level,
                serialize=False,
                format='[{time}] [{level:<8}] [{message}]',
                rotation='1h',
                filter=_RouteFilter().filter_by_loguru
            )

    @classmethod
    def get_handler(cls, entry_point, save_to_file, loguru_ignore):
        cls._init_file_path()

        import loguru

        console = loguru.logger

        def traceback_func(self, level):

            def _traceback(debug_info):
                """from loguru source code"""
                if loguru_ignore and request.path in loguru_ignore:
                    return
                __message = cls._split_msg(origin_msg=debug_info)
                options = (True,) + self._options[1:]
                self._log(level, None, False, options, __message, (), {})

            return _traceback

        def no_traceback_func(self, level):

            def _no_traceback(debug_info):
                """from loguru source code"""
                __message = cls._split_msg(origin_msg=debug_info)
                self._log(level, None, False, self._options, __message, (), {})

            return _no_traceback

        console.debug = no_traceback_func(self=console, level=logging.getLevelName(logging.DEBUG))
        console.info = no_traceback_func(self=console, level=logging.getLevelName(logging.INFO))
        console.warning = no_traceback_func(self=console, level=logging.getLevelName(logging.WARNING))
        console.error = traceback_func(self=console, level=logging.getLevelName(logging.ERROR))
        console.critical = traceback_func(self=console, level=logging.getLevelName(logging.CRITICAL))

        if save_to_file:
            cls._add_file_logger(console=console, entry_point=entry_point)

        return console


class _FileLogger:
    """
        本地日誌檔案
    """

    _TITLE = os.environ.get('SYSTEM_NAME', 'default_log')
    _ABS_PATH = os.path.abspath('.')
    _METHODS = {
        'debug': ['/log/debug_log/', logging.DEBUG],
        'warning': ['/log/warning_log/', logging.WARNING],
        'error': ['/log/error_log/', logging.ERROR],
        'critical': ['/log/critical_log/', logging.CRITICAL]
    }

    @classmethod
    def _init_file_path(cls):
        for key, value in cls._METHODS.items():
            path = value[0]
            os.makedirs(f'{cls._ABS_PATH}{path}', exist_ok=True)

    @staticmethod
    def _get_file_handler(file_name, level=logging.DEBUG):
        console = TimedRotatingFileHandler(
            file_name, when='H', interval=1, backupCount=10000, encoding=None, delay=False, utc=False)
        console.setLevel(level)
        formatter = logging.Formatter('[%(asctime)-s] [%(levelname)-8s] [%(message)s]')
        console.setFormatter(formatter)
        console.addFilter(_RouteFilter())
        return console

    @classmethod
    def get_handlers(cls, entry_point):
        cls._init_file_path()
        console_list = list()
        for key, value in cls._METHODS.items():
            file_handler = cls._get_file_handler(
                file_name=f'{cls._ABS_PATH}{value[0]}{cls._TITLE}.{entry_point}.{key}.log', level=value[1])
            console_list.append(file_handler)
        return console_list


class _PrintLogger:
    """
        print到終端上的
    """

    @staticmethod
    def get_handler(level=logging.DEBUG):
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] [%(message)s]')
        console.setFormatter(formatter)
        console.addFilter(_RouteFilter())
        return console


class _StackLogger:
    """
        堆疊訊息
    """

    _frequency = 1
    _stack = {}  # {<debug_msg>: <callback_method>}
    _monitor = None

    @classmethod
    def _run(cls):
        while True:
            try:
                if not cls._stack:
                    time.sleep(cls._frequency)
                    continue
                temp_dict = cls._stack.copy()
                for msg, method in temp_dict.items():
                    method(msg)
                    cls._stack.pop(msg)
                time.sleep(cls._frequency)
            except Exception as e:
                DebugTool.error(e)
                time.sleep(cls._frequency)

    @classmethod
    def _init(cls):
        cls._monitor = threading.Thread(target=cls._run)
        cls._monitor.start()

    @classmethod
    def push(cls, msg, method):
        if cls._monitor is None:
            cls._init()
        cls._stack.update({
            msg: method
        })


class DebugTool:
    """
        How to start:
            Initial tool in your entry point file.

            if __name__ == '__main__':

                DebugTool.start_logging(__file__)

                ...

        If you need, change config:

            class LoggingConfig:
                _remote = True

            DebugTool.from_object(config=LoggingConfig())
            DebugTool.start_logging(__file__)

        *** error and critical method can logged traceback ***

        How to use:
            DebugTool.<method>(exception=<Exception object>, msg=<message string>)

        Example:

            try:
                ...

            except IOError as e:

                DebugTool.debug(e)
                DebugTool.debug(msg='occur IOError exception')
                DebugTool.debug(e, msg='occur IOError exception')

        Options:

            + do_stack: 是否開啟log堆積功能

    """

    _loguru_logger = None
    _use_loguru = True  # 使用loguru套件

    _logger = None
    _do_print = True
    _save_to_file = True
    _remote = False
    _env = 'develop'
    _settings = {
        'develop': False,
        'release': False,
        'production': False
    }
    _packages = [
        'requests', 'urllib3', 'apscheduler', 'engineio', 'socketio', 'PIL', 'selenium'
    ]

    @classmethod
    def from_object(cls, config):
        _types = {
            '_use_loguru': bool,
            '_do_print': bool,
            '_save_to_file': bool,
            '_remote': bool,
            '_env': str,
            '_settings': dict,
            '_packages': list
        }

        for k, _type in _types.items():
            setting = getattr(config, k, None)
            if setting is None:
                continue
            if type(setting) is not _type:
                raise Exception(f'[{cls.__name__}] [Config Error] {k}: {setting} type should be {_type}')
            setattr(cls, k, setting)

        for k, v in cls._settings.items():
            if type(k) is not str or type(v) is not bool:
                raise Exception(
                    f'[{cls.__name__}] [Config Error] [attr "_settings" type error] '
                    f'key type should be str: {type(k)} | value type should be bool: {type(v)}')

        for name in cls._packages:
            if type(name) is not str:
                raise Exception(f'[{cls.__name__}] [Config Error] value in "_packages" should be str')

        if cls._env not in cls._settings:
            raise Exception(f'[{cls.__name__}] [Config Error] attr "_env" not in "_settings"')

    @classmethod
    def _control_remote(cls):
        cls._remote = cls._settings[cls._env]

    @classmethod
    def _set_loggers(cls, console_list):
        cls._logger = logging.getLogger()
        cls._logger.setLevel(logging.DEBUG)
        for console in console_list:
            cls._logger.addHandler(console)

    @classmethod
    def _shield_info(cls):
        """
            屏蔽套件訊息
        """
        for package in cls._packages:
            logging.getLogger(package).setLevel(logging.WARNING)
        logging.captureWarnings(True)

    @staticmethod
    def _get_debug_schema(msg=None, exception=None, traceback_result=None):
        debug_info = f'<MESSAGE>: {msg} | <EXCEPTION>: {exception} | <TRACEBACK>: \n{traceback_result}'
        return debug_info

    @classmethod
    def _logging(cls, method, exception=None, msg=None, do_traceback=False, do_stack=False):
        traceback_result = traceback.format_exc().strip('\n') if do_traceback else None
        debug_info = cls._get_debug_schema(msg=msg, exception=exception, traceback_result=traceback_result)
        if not do_stack:
            method(str(debug_info))
        else:
            _StackLogger.push(msg=debug_info, method=method)

    @classmethod
    def _logging_by_loguru(cls, method_name, exception=None, msg=None, do_traceback=False, do_stack=False):
        if not cls._loguru_logger:
            return
        cls._logging(
            method=getattr(cls._loguru_logger, method_name),
            exception=exception,
            msg=msg,
            do_traceback=do_traceback,
            do_stack=do_stack
        )

    @classmethod
    def start_logging(cls, entry_point, loguru_ignore=list()):
        entry_point = os.path.basename(entry_point)
        cls._control_remote()
        console_list = list()
        if cls._do_print:
            console_list.append(_PrintLogger.get_handler())
        if cls._save_to_file:
            console_list.extend(_FileLogger.get_handlers(entry_point=entry_point))
        if cls._remote:
            console_list.append(_FluentLogger.get_handler(entry_point=entry_point))
        cls._set_loggers(console_list=console_list)
        cls._shield_info()

        # 非測試環境強制關閉loguru
        if cls._env == 'develop' and cls._use_loguru:
            cls._loguru_logger = _LoguruLogger.get_handler(
                entry_point=entry_point,
                save_to_file=cls._save_to_file,
                loguru_ignore=loguru_ignore
            )

    @classmethod
    def _validate(cls):
        if not cls._logger:
            raise Exception('DebugTool need to been initialized.')

    @classmethod
    def debug(cls, exception=None, msg=None, do_stack=False):
        cls._validate()
        cls._logging(method=cls._logger.debug, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)
        cls._logging_by_loguru(
            method_name=cls.debug.__name__, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)

    @classmethod
    def info(cls, exception=None, msg=None, do_stack=False):
        cls._validate()
        cls._logging(method=cls._logger.info, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)
        cls._logging_by_loguru(
            method_name=cls.info.__name__, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)

    @classmethod
    def warning(cls, exception=None, msg=None, do_stack=False):
        cls._validate()
        cls._logging(method=cls._logger.warning, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)
        cls._logging_by_loguru(
            method_name=cls.warning.__name__, exception=exception, msg=msg, do_traceback=False, do_stack=do_stack)

    @classmethod
    def error(cls, exception=None, msg=None, do_stack=False):
        cls._validate()
        cls._logging(method=cls._logger.error, exception=exception, msg=msg, do_traceback=True, do_stack=do_stack)
        cls._logging_by_loguru(
            method_name=cls.error.__name__, exception=exception, msg=msg, do_traceback=True, do_stack=do_stack)

    @classmethod
    def critical(cls, exception=None, msg=None, do_stack=False):
        cls._validate()
        cls._logging(method=cls._logger.critical, exception=exception, msg=msg, do_traceback=True, do_stack=do_stack)
        cls._logging_by_loguru(
            method_name=cls.critical.__name__, exception=exception, msg=msg, do_traceback=True, do_stack=do_stack)
