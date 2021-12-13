import time

import click
import nidaqmx
from influx_line_protocol import Metric, MetricCollection


class NIlog:

    def __init__(self, tasks: list):
        self.tasks = tasks

    def __enter__(self):
        self.loaded_tasks = self.load_tasks()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.loaded_tasks:
            for task in self.loaded_tasks:
                task.close()

    def load_tasks(self):
        return [(nidaqmx.system.storage.persisted_task.PersistedTask(task)).load() for task in self.tasks]

    def start(self):
        if self.loaded_tasks:
            for task in self.loaded_tasks:
                task.start()

    def read(self, measurement: str = "telegraf_nidaqmx"):

        if self.loaded_tasks:

            collection = MetricCollection()

            for loaded_task in self.loaded_tasks:

                values = self.make_list(loaded_task.read())
                fields = self.make_list(loaded_task.channel_names)
                metrics = {key: val for key, val in zip(fields, values)}
                devs = [ dev.name for dev in self.make_list(loaded_task.devices) ]
                name = loaded_task.name

                for key, val in metrics.items():

                    metric = Metric(f"{measurement}")
                    # metric.with_timestamp(1465839830100400200)
                    metric.add_tag('task', f'{name}')
                    for i, dev in enumerate(devs):
                        metric.add_tag(f'dev{i}', dev)
                    metric.add_tag('channel', f'{key}')
                    metric.add_value('value', val)
                    collection.append(metric)

            return collection

    @staticmethod
    def make_list(data):
        return data if isinstance(data, list) else [ data, ]


@click.command()
@click.option('--measurement', default="telegraf_nidaqmx",
              help='The name given to the measurement for Influx line protocol.')
@click.option('--task', required=True, multiple=True,
              help="Task as labeled in NI MAX, e.g. --task voltage. Note multiple Tasks are acceptable, e.g. --task "
                   "voltage --task current.")
@click.option('--interval', default=1.0,
              help='Interval in seconds between Task reads.')
@click.option('--test/--no-test', default=False,
              help='Run with --test flag to read task(s) once.')
def cli(task, interval, test, measurement):
    '''

    A simple CLI to be used as an external Telegraf plugin to acquire data from NI-DAQmx Tasks
    That have been configured in NI MAX.

    '''
    tasks = list(task)

    if test:
        with NIlog(tasks) as t:
            t.start()
            click.echo(t.read())

    else:
        with NIlog(tasks) as t:
            t.start()
            while True:
                metrics = t.read(measurement=measurement)
                print(metrics, flush=True)
                time.sleep(interval)


if __name__ == '__main__':
    cli()
