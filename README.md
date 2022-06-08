# telegraf_nidaqmx

External Telegraf plugin to acquire data from NI-DAQmx Tasks

## Installation

```bash
pip install --upgrade git+https://github.com/pyfonics/telegraf_nidaqmx.git
```

This should install the CLI `telegraf-nidaqmx`. Add the executable to system PATH if required.

## Usage

Run the following command in a command prompt to show the help text.

```

telegraf-nidaqmx --help

```

Once NI-DAQmx tasks have been configured in NI MAX utility, test that `telegraf-nidaqmx` can read the NI-DAQmx tasks.

```
telegraf-nidaqmx --task ExampleTask1 --task ExampleTask2 --interval 1 --test
```


The Telegraf plugin [`inputs.execd`](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/execd) is used to collect data from `telegraf-nidaqmx`.

An example configuration is shown below:

```toml
[[inputs.execd]]

  command = ["telegraf-nidaqmx", "--task", "ExampleTask1", "--task", "ExampleTask2", "--interval", "0.5"]
  signal = "none"
  restart_delay = "10s"
  data_format = "influx"

```

