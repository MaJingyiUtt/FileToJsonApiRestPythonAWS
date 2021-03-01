"""This file contains all the constants, to protext them from changing value."""

class Const(object):
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:  # check if the contant is already defined
            raise self.ConstError("Can't change const.%s" % name)
        if not name.isupper():  # check if the constant name is capitalized.
            raise self.ConstCaseError('const name "%s" is not all supercase' % name)

        self.__dict__[name] = value


const = Const()
const.ERROR_MESSAGE_NO_FILE = "Sorry, no file is uploaded. "
const.ERROR_MESSAGE_EXTENSION_NOT_ALLOWED = (
    "Sorry, the extension of your file is not allowed in this app."
)
