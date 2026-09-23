---
title: On Designer Assertions in SystemVerilog
layout: post
---

At lowRISC I picked up the habit of including behavioural assertions in my RTL -- things like:
```verilog
// Assert the AXI Stream is standard compliant

// valid should stay high until the downstream is ready
`ASSERT(TxAxisValidStaysUntilHandshake_A,
    tx_axis_o.valid && !tx_axis_tready_i |=> tx_axis_o.valid
);
// data and last should stay the same until the downstream is ready
`ASSERT(TxAxisInvariantUntilHandshake_A,
    tx_axis_o.valid && !tx_axis_tready_i |=> $stable(tx_axis_o.data) && $stable(tx_axis_o.last)
);

// these `ASSERT macros are a lowRISC convention for creating clocked asserted properties
```

These aren't remotely a substitute for proper testing, but they do provide invaluable benefits:

* When something goes wrong, usually an assertion will fail that points you right to the source of the error. This massively accelerates the debugging process
* As a designer, I often worry a great deal about somebody driving my design incorrectly because they haven't read the documentation. These assertions provide an assurance that if they try to do so, it will fail, quickly and catastrophically.

## Why I love these
It seems to me that the greatest source of verification failures arises from not adhering precisely to standards. For example, MOST AXI-Stream sinks will not sample the data until the valid signal is asserted -- however, the specification does not state that they MUSTN'T. The former makes it tempting for those driving an AXI-Stream source to allow the data to change value before being sampled, even though this is explicitly disallowed by the specification. These kinds of bugs usually go unnoticed because both blocks independently may adhere to their own interpretation of the specification (one of which is incorrect) and therefore pass their own tests, and integration snags are more likely to remain hidden for a long period. For this reason, I find great reassurance in being able to create my block and explicitly declare "you must drive these inputs in this way or this block will not behave correctly". To this end, I like to put assertions on the inputs to my blocks.

## Should assertions go on the outputs, though?
Assertions can slow down simulation, so best not to have them duplicated if you can avoid it. The question then is, who is responsible for putting in assertions -- the driver or the consumer?

At lowRISC, the answer is the driver. One possible justification for this is that a single bus or net could have many consumers, and it would be wasteful for them all to individually put checks on it.

However, relying on the driver has one absolutely massive issue: trust. I do not trust that whoever is using my block will remember to put assertions on their outputs, or even use it in a protocol-compliant way. I would very much prefer to put assertions on the input *requiring* that it be used correctly.

## Reusable assertion moduels for standard protocols
Hopefully the title says it all, here. Of course there are standard bus and data protocols (beyond AXI Stream) that will be used in many parts of a design. To avoid code repetition, it is reasonable to create a reusable module. There are broadly four ways in which this moduel can be applied:

* The block consuming the bus is responsible for including the assertions
    * Allows the designer of a block to strictly define how that block can be driven
    * Risk of redundancy if multiple blocks share that bus
* The block driving the bus is responsible for including the assertions
    * Guarantee of no redundant assertions
    * Designers have no way of assertion that there design will actually be driven correctly, instead relying on the consumers of their design to identify and implement the correct protocol
* The parent block where he bus signal(s) are instantiated is responsible for including the assertions
    * Similar to the above.
    * Arguably a cleaner code practice -- the bus is an interconnect between modules, so its behaviour should be governed as such
* The testbench should `bind` an assertion module to one of the below

All four provide the same functionality but each offer a tradeoff of cleaner code and certainty.

In fact these assertions occupy a similar role in the design process to coverage trackers and monitors. It may therefore be appropraite to take a page from UVM's book with respect to code style and organisational practice and use the 'bind' keyword.
