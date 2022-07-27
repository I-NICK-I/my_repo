# -*- coding: utf-8 -*-
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches

from collections import defaultdict as dd
from contextlib import suppress
from copy import deepcopy
from typing import Any

from loguru import logger


def has_dicts(dict_values: list):
    """Служебная функция, убедиться что в списке значений есть словари"""
    return any(True if isinstance(_, dict) else False for _ in dict_values)


def has_lists(dict_values: list):
    """Служебная функция, убедиться что в списке значений есть списки"""
    return any(True if isinstance(_, list) else False for _ in dict_values)


class DictHelper:
    def __init__(self, dictionary: dict):
        self.dictionary = dictionary

    def __str__(self):
        return 'DictHelper is made for deep search for one/few keys, values,' \
               'to make shure key and value in dict, and other..'

    def __repr__(self):
        return 'DictHelper is made for deep search for one/few keys, values,' \
               'to make shure key and value in dict, and other..'

    def key_value_is_in_dict(self, key: str, value: Any,
                             dictionary: dict) -> bool:
        """
        Функция проверяет что полученные ключ и значение есть в словаре
        """
        for item in dictionary:
            item_value = dictionary[item]
            with suppress(KeyError):
                if item_value == value:
                    return True

            if isinstance(item_value, dict):
                if self.key_value_is_in_dict(key, value, item_value):
                    return True
                continue

            if isinstance(item_value, list):
                for sub_item in item_value:

                    if isinstance(sub_item, dict):
                        if self.key_value_is_in_dict(key, value, sub_item):
                            return True
                        continue

                    if isinstance(value, list):
                        for sub_value in value:
                            if sub_value in item_value:
                                return True
                    else:
                        if value in item_value:
                            return True
        return False

    def first_value_of_key(self, key: str, d: dict = None,):
        if not d:
            d = self.dictionary
        return list(
            self.all_values_by_key(some_dict=d, some_key=key).values())[0][0]

    def first_value_of_key2(self, key: str, d: dict = None,):
        if not d:
            d = self.dictionary
        result = None
        temp_dict = self.all_values_by_key(some_dict=d, some_key=key)
        if temp_dict:
            value = temp_dict[key]
            result = value[0] if len(value) > 0 else value
        return result

    def all_values_by_key(self, some_key: str, some_dict: dict = None):
        """Обёртка над методом, позволяющая не тащиить из памяти прошлые
        результаты вызовов метода"""
        if not some_dict:
            some_dict = self.dictionary
        temp_dict = self._all_values_by_key(some_dict=some_dict,
                                            some_key=some_key)
        if isinstance(temp_dict, bool):
            temp_dict = dict()
        uniq_dict_copy = dict(deepcopy(temp_dict))
        temp_dict.clear()
        return uniq_dict_copy

    def _all_values_by_key(self, some_dict: dict,
                           some_key: str,
                           values_by_key: dict = dd(list),
                           parent_key: str = None):
        """
        Функция возвращает все значения соответствующие переданному ключу
        :param some_dict: словарь используемый для поиска
        :param some_key: ключ по которому производится поиск
        :param values_by_key: словарь для наполнения
        :param parent_key: родительский ключ (используется при рекурсии)
        :returns: словарь {key: [value1, value2..]} или False
        :rtype: dict / False
        """

        for k, v in some_dict.items():
            if k == some_key:
                founded = some_dict[k]
                if parent_key:
                    values_by_key[f'{parent_key} > {some_key}'].append(founded)
                    continue
                values_by_key[some_key].append(founded)

            k_list, v_list = list(some_dict.keys()), list(some_dict.values())
            if (k not in k_list and not has_dicts(v_list)
                    and not has_lists(v_list)):
                break
            if parent_key:
                parent_key = k
            if isinstance(v, dict):
                self._all_values_by_key(some_dict=v,
                                        some_key=some_key,
                                        parent_key=parent_key)

            if isinstance(v, list):
                _ = [self._all_values_by_key(
                    some_dict=i, some_key=some_key, parent_key=parent_key)
                    for i in v if isinstance(i, dict)]

        return values_by_key or False

    def all_keys_by_value(self, some_dict: dict, some_value: str,
                          answer: dd = dd(list)):
        """
        Функция возвращает все ключи соответствующие переданному значению
        :param some_dict: словарь используемый для поиска
        :param some_value: ключ по которому производится поиск
        :param answer: словарь для наполнения
        :returns: словарь {value: [key1, key2, ..]} или False
        :rtype: dict / False
        """
        for k, v in some_dict.items():
            if v == some_value:
                answer[some_value].append(k)

            _, v_list = list(some_dict.keys()), list(some_dict.values())
            if (v not in v_list and not has_dicts(v_list)
                    and not has_lists(v_list)):
                break

            if isinstance(v, dict):
                self.all_keys_by_value(v, some_value)

            if isinstance(v, list):
                _ = [self.all_keys_by_value(i, some_value) for i in v
                     if isinstance(i, dict)]

        return answer or False

    def two_keys_on_one_lvl(self, dict_: dict, key1: str,
                            key2: str, answer: dd = dd(list),
                            lvl: int = 0):
        """
        Функция проверяет что два полученных ключа находятся на одном уровне
         вложенности в полченном словаре
        :param dict_: словарь для поиска
        :param key1: первый из двух ключей
        :param key2: второй из двух ключей
        :param answer: словарь в котором ключ - это уровень вложенности,
         а значение это пары ключ-значение
        :param lvl: уровегь вложенности (используется для рекурсии)
        :returns: словарь {lvl_0: [{key1: abc, key2: 123}] }
        :rtype: dict / False
        """
        range_ = len(dict_) - 1
        for _ in range(range_):
            if len(dict_) == 0:
                break
            keys_list, values_list = list(dict_.keys()), list(dict_.values())

            if key1 in keys_list and key2 in keys_list:
                answer[f'lvl_{lvl}'].append({
                    key1: dict_.pop(key1),
                    key2: dict_.pop(key2)
                    })

            if (key1 not in keys_list or key2 not in keys_list) \
                    and not has_dicts(values_list) \
                    and not has_lists(values_list):
                break
            lvl += 1
            for value in dict_.values():
                if isinstance(value, dict):
                    self.two_keys_on_one_lvl(value, key1, key2, lvl=lvl)

                if isinstance(value, list):
                    _ = [self.two_keys_on_one_lvl(item, key1, key2, lvl=lvl)
                         for item in value if isinstance(item, dict)]
            lvl -= 1
        return answer or False

    def full_paths_list(self, dictionary: dict, parent_key: str = None,
                        value_type: Any = False):
        """
        Функция проходит по словарю и собирает полный индивидуальный путь
         до значений формата int, float, str
        :param dictionary: словарь для разбора
        :param parent_key: родительский ключ, параметр нужен для рекурсии
        :param value_type: флаг возврата типа значения
        :returns: список с полными путями до ключей формата:
        [key][deeper_ker][0..N] = value ☺ <value_type>
        где [0..N] индекс в случае с парсинга списка
        :rtype: list
        """
        path = list()

        for key, value in dictionary.items():
            current_key = f'[{key}]'
            val_type = type(value)
            if parent_key:
                current_key = f'{parent_key}{current_key}'
            if isinstance(value, list) and value:
                enum_val = enumerate(value)
                value = {str(num): val for num, val in enum_val}
            elif not value:
                value = str(value)

            if isinstance(value, dict):
                dict_part = self.full_paths_list(value, parent_key=current_key)
                _ = [path.append(j) for i, j in enumerate(dict_part)]
                dict_part.clear()

            else:
                result = f'{current_key} = {value}'
                if value_type:
                    result += f' ☺ {val_type}'
                path.append(result)

        return path

    def check_keys_on_same_lvl(self, dictionary: dict, keys: list,
                               parent_key: str = None, exp_amount: int = None
                               ):
        """
        Функция проверяет что все ключи и полученного списка находятся на
         одном уровне вложенности в полученном словаре
        :param dictionary: словарь для поиска
        :param keys: список искомых ключей
        :param parent_key: родительский ключ - на случай если потребуется
         узнать где встречаются все полученные ключи
        :param exp_amount: ожидаемое количество ключей
        :returns: пройдена проверка или нет
        :rtype: bool
        """

        temp_dict = deepcopy(dictionary)
        # по мере продвижения вглубь все неподходящие ключи будут удаляться
        # из словаря как тригер для выхода из функции и для экономии памяти
        while len(temp_dict) != 0:

            keys_list = list(temp_dict.keys())
            intersection = len(set(keys_list) & set(keys))
            if not exp_amount or exp_amount > len(keys):
                logger.debug('Expected amount = <%s> must be less than or '
                             'equal to amount of keys <%s>. Search continues '
                             'with amount of keys <%s>',
                             exp_amount, len(keys), len(keys))
                exp_amount = len(keys)

            if intersection == exp_amount:
                return True

            if any(type(val) in (dict, list) for val in temp_dict.values()):
                temp_dict = {x: y for x, y in temp_dict.items()
                             if type(y) in (dict, list)}

            for temp_key, temp_value in temp_dict.items():
                if isinstance(temp_value, list):
                    temp_value = dict(enumerate(temp_value))

                parent_key = temp_key
                if isinstance(temp_value, dict):
                    if self.check_keys_on_same_lvl(
                            temp_value, keys, parent_key=parent_key,
                            exp_amount=exp_amount):
                        return True

                temp_dict.pop(temp_key)
                break
        return False