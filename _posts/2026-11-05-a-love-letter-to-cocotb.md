---
title: A love letter to CocoTB
layout: post
---
One of the first questions I asked myself starting out in the semiconductor industry: If a testbench doesn't describe hardware, why are they written in a hardware description language, SystemVerilog?

The answer of course is that SystemVerilog is not just a HDL, it is also an object-oriented languages, and includes a language for writing properties in formal notation. This is an [awful mess]({% post_url 2026-07-30-problems-with-sv %}) of three languages mushed into one.

Tests are *software*. They run procedurally, albeit with multiple threads. It stands to reason that they ought to be written in a conventional programming language. This is where CocoTB comes in: a **Python** package that provides the means to drive and monitor signals in an RTL design.

In CocoTB, tests look something like this:
```python
@cocotb.test()
async def my_test(_dut):
    dut = DUT_Wrapper(_dut)

    # Start up and configure the DUT
    dut.start_clock()
    dut.reset()
    dut.configure(loopback=True,mode=LOW_POWER)

    # Wait 10 clock cycles
    for _ in range(10):
        await dut.clock_edge()

    assert dut.read_data() == EXPECTED_DUT_BASE_CASE
```

With the full power of Python at your fingertips, you can wrap as many abstraction layers are you'd like around the DUT, interface with whatever complex third party packages or tools, and do so very efficiently with the aid of Python's fantastic ecosystem.

Of course, I am biased because I know Python extremely well and know very little about using SystemVerilog for verification. I am aware that these same abstraciton layers and third-party tools are possible in SystemVerilog, but I would argue more cumbersome.

A laundry list of reasons why I love CocoTB:

* Access to the Python ecosystem of package to aid in modelling the DUT (e.g. DSP is very easy in Python)

* Access to the Python ecosystem for infrastructural tools like linting, test frameworks, etc.

* Increased object-oriented programming capabilities, compared to SystemVerilog

* Behavioural modelling of your DUT is better done in a language other than SystemVerilog to prevent the same bug from being introduced in both the DUT and the model. This is possible in SystemVerilog using the C DPI, but not straightforward.
