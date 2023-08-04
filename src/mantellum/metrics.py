"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://github.com/nicc777/mantellum/blob/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import time
import json
import copy
from mantellum.logging_utils import get_logger
from mantellum.date_and_time_utils import get_utc_timestamp


decorator_logger = get_logger()


class Dimension:

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            'Name': '{}'.format(self.name),
            'Value': '{}'.format(self.value),
        }


class Dimensions:

    def __init__(self):
        self.dimensions = list()

    def add_dimension(self, dimension: Dimension):
        self.dimensions.append(dimension)

    def to_dict(self):
        items = list()
        for dimension in self.dimensions:
            items.append(dimension.to_dict())
        return {
            'Dimensions': items,
        }


class MetricRecords:

    def __init__(self, name: str, metric_unit: str='Count', storage_resolution: int=60):
        self.name = name
        self.metric_unit = metric_unit
        self.storage_resolution = storage_resolution
        self.records = list()

    def record_dimension_value(self, dimensions: Dimensions, recorded_value: object, override_timestamp_value: float=get_utc_timestamp(with_decimal=True)):
        self.records.append(
            {
                'Dimensions': dimensions,
                'Timestamp': override_timestamp_value,
                'Value': recorded_value,
            }
        )

    def to_dict(self):
        data = list()
        for record in self.records:
            data.append(
                {
                    'MetricName': self.name,
                    'Dimensions': record['Dimensions'].to_dict()['Dimensions'],
                    'Timestamp': record['Timestamp'],
                    'Value': record['Value'],
                    'Unit': '{}'.format(self.metric_unit),
                    'StorageResolution': self.storage_resolution
                }
            )
        return {
            'MetricRecords': data
        }


class MetricPushHandlerBaseClass:

    def __init__(self, handler_function_implementation: object):
        self.positional_parameter_values = list()
        self.named_parameter_values = dict()
        self.func = handler_function_implementation

    def add_positional_parameter(self, value: object):
        self.positional_parameter_values.append(value)

    def add_named_parameter(self, name: str, value: object):
        self.named_parameter_values[name] = value

    def push_metric(self, record: MetricRecords, positional_parameter_overrides: list=None, named_parameter_overrides: dict=None):
        final_args = self.positional_parameter_values
        if positional_parameter_overrides is not None:
            final_args = positional_parameter_overrides
        final_kwargs = self.named_parameter_values
        if named_parameter_overrides is not None:
            final_kwargs = named_parameter_overrides
        final_kwargs['metric_record'] = record
        try:
            self.func(*final_args, **final_kwargs)
        except:
            traceback.print_exc()


def dummy_metric_push_handler(metric_records: MetricRecords):
    print('dummy_metric_push_handler(): METRIC RECORDS as JSON: {}'.format(json.dumps(metric_records.to_dict(), default=str)))


class DummyMetricPushHandler(MetricPushHandlerBaseClass):

    def __init__(self):
        super().__init__(handler_function_implementation=dummy_metric_push_handler)


class MetricWrapper:
    
    def __init__(self, namespace: str='Custom/Undefined', metric_name: str='UndefinedMetric', push_metric_handler: MetricPushHandlerBaseClass=DummyMetricPushHandler()):
        self.namespace = namespace
        self.metric_name = metric_name
        self.records = list()
        self.push_metric_handler = push_metric_handler

    def add_metric_record(self, record: MetricRecords):
        self.records.append(record)

    def push_metrics(self, clear_records_after_push: bool=True):
        for record in self.records['MetricRecords']:
            self.push_metric_handler.push_metric(record=record)
        if clear_records_after_push is True:
            self.records = list()


class MeasuredFunctionCallHandler:

    def __init__(
        self,
        application_name: str,
        function_name: str,
        registered_function: object,
        push_metric_handler: MetricPushHandlerBaseClass=DummyMetricPushHandler()
    ):
        self.function_name = function_name
        self.metric_wrapper = MetricWrapper(
            namespace='Custom/Applications/FunctionCalls', 
            metric_name=function_name,
            push_metric_handler=push_metric_handler
        )
        self.registered_function = registered_function

    def call_function(
        self,
        args: list=list(),
        kwargs: dict=dict(),
        absorb_exception: bool= True,
        push_metrics_after_call: bool=True,
        clear_metric_records_after_push: bool=True
    ):
        start_time = get_utc_timestamp(with_decimal=True)

        exception_raised = False
        exception_object = None
        result = None
        try:
            result = self.registered_function(*args, **kwargs)
        except Exception as e:
            exception_raised = True
            exception_object = copy.deepcopy(e)

        finish_time = get_utc_timestamp(with_decimal=True)
        diff_time = finish_time - start_time
        record = MetricRecords(metric_unit='Seconds', storage_resolution=60)
        record.record_dimension_value(
            dimensions=[
                Dimension(name='ApplicationName', value=self.application_name),
                Dimension(name='FunctionName', value=self.function_name),
            ],
            recorded_value=diff_time,
            override_timestamp_value=finish_time
        )
        self.metric_wrapper.add_metric_record(record=record)
        if exception_raised is True and absorb_exception is False and exception_object is not None:
            raise exception_object

        if push_metrics_after_call is True:
            self.metric_wrapper.push_metrics(clear_records_after_push=clear_metric_records_after_push)

        return result


