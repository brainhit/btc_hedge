# -*- coding=utf-8 -*-


class ExceptionSupportUnicode(Exception):

    def __init__(self, message):
        super(ExceptionSupportUnicode, self).__init__(message.encode('utf-8'))


class ParamsError(ExceptionSupportUnicode):
    pass


class ApiRequestError(ExceptionSupportUnicode):
    pass


class BinanceAPIException(ExceptionSupportUnicode):
    pass


class BinanceRequestException(ExceptionSupportUnicode):
    pass


class HuoBiApiException(ExceptionSupportUnicode):
    pass


class NotEnoughCoinError(ExceptionSupportUnicode):
    pass


class InitialError(ExceptionSupportUnicode):
    pass


class CombinationNotExistError(ExceptionSupportUnicode):
    pass


class OKExAPIException(ExceptionSupportUnicode):
    pass


class OKExRequestException(ExceptionSupportUnicode):
    pass


class SubChannelError(ExceptionSupportUnicode):
    pass
