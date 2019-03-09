import pickle

from os import listdir

from os.path import isfile, join, basename, splitext

import re

user_data_folder = r'persistence/'


def get_file(user_id):
    return user_data_folder + str(user_id) + r".pickle"


def save_user_data(user_id, user_data):
    with open(get_file(user_id), "wb") as output_file:
        pickle.dump(user_data, output_file)


def get_user_data(user_id):
    with open(get_file(user_id), "rb") as input_file:
        return pickle.load(input_file)


def exist_user_data(user_id):
    return isfile(get_file(user_id))


def get_user_data_or_create(user_id):
    if exist_user_data(user_id):
        return get_user_data(user_id)
    else:
        save_user_data(user_id, {})
        return {}


class UserData:

    def __init__(self, user_id):
        self.id = user_id
        self.data = get_user_data_or_create(user_id)

    def __getitem__(self, name):
        if name in self.data:
            return self.data[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def get(self, name, default=''):
        try:
            return self.__getitem__(name)
        except AttributeError:
            return default

    def init(self, name, value=''):
        try:
            self.__getitem__(name)
        except AttributeError:
            self.__setitem__(name, value)

    def __setitem__(self, name, value):
        self.data[name] = value
        save_user_data(self.id, self.data)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except AttributeError:
            return False

    def __delitem__(self, name):
        if name in self.data:
            del self.data[name]
            save_user_data(self.id, self.data)
        else:
            raise AttributeError("No such attribute: " + name)


def get_user(update):
    return update.message.from_user


def user_data(arg):
    try:
        user_id = get_user(arg).id
    except AttributeError:
        user_id = arg
    return user_data_from_id(user_id)


import collections
import functools


class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


@memoized
def user_data_from_id(user_id):
    return UserData(user_id)


def get_saved_ids():
    return [int(splitext(basename(f))[0]) for f in listdir(user_data_folder) if isfile(join(user_data_folder, f))]


