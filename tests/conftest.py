# -*- coding: utf-8 -*-
import csv
import inspect
from loguru import logger
import pytest
import re
import time

from datetime import datetime
from math import ceil
from os import getenv, environ, path, mkdir, getcwd, listdir


counter = 0


@pytest.fixture(autouse=True)
def test_iteration():
    """
    Фикстура пишет номер итерации теста, прибавляя каждый раз +1, пока не
     встретит следующий тест (требуется для составления отчёта), помещает в
     переменные окружения имя кейса tmj4 и имя кейса в python
    """
    global counter
    stack = inspect.stack()
    item = stack[29].frame.f_locals['item'].originalname
    case_markers = stack[29].frame.f_locals['item'].own_markers
    if case_markers:
        case_name = [mark.name for mark in case_markers if
                     mark.name.startswith('T')]
        case_name = case_name[0] if len(case_name) > 0 else 'unmarked_case'
    else:
        case_name = 'unmarked_case'
    environ['TEST_NAME'] = item
    environ['TM4J_CASE'] = case_name
    environ['RUN_CASES'] = getenv('RUN_CASES') + f' {case_name}'

    try:
        next_item = stack[29].frame.f_locals['nextitem'].originalname
    except AttributeError:
        next_item = item

    environ["TEST_ITERATION"] = str(counter)
    counter += 1

    if item != next_item:
        counter *= 0


@pytest.fixture
def expect(request):
    def do_expect(expr, msg=''):
        if not expr:
            _log_failure(request.node, msg)
            environ['testrun_is_failed'] = 'True'
            if getenv('run_report'):
                _write_failure(request.node, msg)

    return do_expect


def _log_failure(node, msg=''):
    # Get filename, line, and context
    (filename, line, _, context_list) = inspect.stack()[2][1:5]
    filename = path.basename(filename)
    if isinstance(msg, str) and msg:
        context = msg
    else:
        context = context_list[0].strip()
        match = re.search(r'^expect\((.+)\)$', context)
        context = match.group(1) if match else context
    entry = f'Failed condition: "{context}"\n{filename}:{line}\n'
    # Add entry
    if not hasattr(node, 'failed_expect'):
        node.failed_expect = []
    node.failed_expect.append(entry)


def _write_failure(node, msg=None):
    """
    Функция собирает инфу о функции в рамках которой был вызван expect,
     на какой линии этот expect, полное условие падения, текст ассерта,
     параметры теста, имя теста, маркер теста начинающийся с "Т", и записывает
     эту собранную информацию в .csv файл отчёта
    """
    testcase = getenv('TM4J_CASE', 'default_case')
    testrun = getenv('TM4J_RUN', 'default_run').upper()
    run_start_time = getenv('RUN_START_TIME', None)
    if testrun and run_start_time:
        testrun += f'_{run_start_time}'
    test_name = getenv('TEST_NAME')
    filename_called = inspect.stack()[2].filename
    func_called = inspect.stack()[2].function
    st = inspect.stack()

    for _, outer_frame in enumerate(st):
        if test_name in outer_frame.function:
            test_params = outer_frame.frame.f_locals
            break

    assert_filename = inspect.stack()[2][1]
    assert_line = al = inspect.stack()[2][2]

    context = inspect.stack()[2][4][0].strip()
    match = re.search(r'^expect\((.+)\)$', context)
    condition = match.group(1) if match else context

    if getenv('run_report').lower() == 'max':
        with open(assert_filename, 'r', encoding='utf8') as afile:
            f = afile.readlines()
            condition = ''
            for ass_line in f[al - 1:al + 4]:
                ass_line = ass_line.strip()
                if not ass_line:
                    break
                ass_line = ass_line.replace(';', ',')
                condition += ass_line
            afile.close()
            del (assert_filename, al, f, afile)

    assert_text = ''
    if isinstance(msg, str):
        msg = msg.strip()
        if msg and ':' in msg:
            idx = msg.index(':') + 1
            msg = msg[idx:].replace(';', ',').strip()
        assert_text += msg

    iteration = getenv('test_iteration')
    title = ['TM4J', 'Test_in_python', 'Iteration', 'Func_called_expect',
             'Line', 'Condition', 'Assert_text', 'File_called_expect']
    row_template = [testcase, test_name, iteration, func_called, assert_line,
                    condition, assert_text, filename_called]

    for key, value in test_params.items():
        if type(value) is bool:
            if value: value = 'True'
            else: value = 'False'

        elif value is None: value = 'None'
        elif value == '': value = "''"

        elif type(value) in (dict, tuple, list, str, int, float):
            value = f'{value=}'.split('=')[1]
            value = value.replace('\n', '').replace(';', ',')
        else: continue
        row_template.append(value)
        title.append(f'test_param: {key.capitalize()}')

    rows = [row_template]
    report_folder = f'{getcwd()}\\tmp_reports\\{testrun}'
    environ['REPORTS_PATH'] = report_folder
    report = f'{report_folder}\\{testcase}.csv'
    general_report = f'{report_folder}\\{testrun}_full.csv'

    if not path.exists(report_folder):
        mkdir(report_folder)

    if not path.exists(report):
        rows.insert(0, title)

    for rep in (report, general_report):
        with open(rep, 'a+',
                  encoding='cp1251',
                  newline=''
                  ) as file:
            csv_writer = csv.writer(file,
                                    delimiter=';',
                                    quotechar=" ",
                                    quoting=csv.QUOTE_MINIMAL,
                                    dialect='excel')
            for row in rows:
                csv_writer.writerow(row)
            file.close()


def make_report():
    """
    Фикстура пишет csv отчёт со временем начала и окончания теста,
     длительностью, номером итерации, именем теста в коде, результатом,
     началом и окончанием в формате unixtime
    """
    run_start_time = str(datetime.now()).replace(':', '-') \
                         .replace(' ', '_')[:16]
    if not getenv('RUN_START_TIME'):
        environ['RUN_START_TIME'] = run_start_time
    start_time = datetime.now()
    start_unixtime = time.time()
    start_time_str = str(start_time)
    start_unixtime_str = str(time.time())[:13]
    item_frame = [_ for _ in inspect.stack()
                  if _.function == 'pytest_runtestloop'][0]
    test_name = item = item_frame.frame.f_locals['item'].originalname
    case_markers = item_frame.frame.f_locals['item'].own_markers
    if case_markers:
        test_markers = sorted([i.name for i in case_markers])
        markers = str(test_markers).replace("'", "")[1:-1]
    else:
        markers = '~no_pytest_mark'

    try:
        next_item = item_frame.frame.f_locals['nextitem'].originalname
    except AttributeError:
        next_item = item

    iteration = str(counter)
    counter += 1

    if item != next_item:
        counter *= 0

    yield

    result = 'Pass'
    result_item = [_ for _ in inspect.stack() if
                   _.function == 'runtestprotocol'][0]
    results_reports = result_item.frame.f_locals['reports'] if \
        'reports' in result_item.frame.f_locals.keys() else None
    if results_reports:
        is_failed = any([result.failed for result in results_reports])
        if is_failed:
            result = 'Fail'

    end_time = datetime.now()
    end_unixtime = time.time()
    end_time_str = str(end_time)
    end_unixtime_str = str(end_unixtime)[:13]
    title = ['Start_time', 'End_time', 'Duration_ms', 'Test_name', 'Iteration',
             'Result', 'Markers', 'Unixtime_start', 'Unixtime_end']
    duration = f'{ceil((end_unixtime - start_unixtime) * 1000)}'
    row_template = [start_time_str, end_time_str, duration, test_name,
                    iteration, result, markers, start_unixtime_str,
                    end_unixtime_str]
    rows = [row_template]
    folder_name = f'TESTRUN_{getenv("RUN_START_TIME")}'
    report_folder = f'{getcwd()}/tmp_reports/{folder_name}'
    general_report = f'{report_folder}/REPORT_{getenv("RUN_START_TIME")}.csv'

    if getenv('make_report') == 'erase':
        from shutil import rmtree
        reports_folder = f'{getcwd()}\\tmp_reports'
        dirs = listdir(reports_folder)
        for dir_ in dirs:
            if dir_.startswith('TESTRUN_'):
                rmtree(f'{reports_folder}\\{dir_}')
        now_dirs = listdir(reports_folder)
        who_deleted = set(dirs) - set(now_dirs)
        logger.info('Из tmp_reports была удалены: %s', who_deleted)
        environ['make_report'] = ''

    if not path.exists(report_folder):
        mkdir(report_folder)

    if not path.exists(general_report):
        rows.insert(0, title)

    for rep in (general_report,):
        with open(rep, 'a+',
                  encoding='cp1251',
                  newline=''
                  ) as file:
            csv_writer = csv.writer(file,
                                    delimiter=';',
                                    quotechar=" ",
                                    quoting=csv.QUOTE_MINIMAL,
                                    dialect='excel')
            for row in rows:
                csv_writer.writerow(row)
            file.close()
