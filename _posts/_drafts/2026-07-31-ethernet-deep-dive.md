---
title: An Unnecessarily Detailed Analysis and Review of the lowRISC Ethernet IP Project
layout: post
---
Today was my last day interning at lowRISC C.I.C.
In my time there, I worked primarily on an [open-source Ethernet interface](https://github.com/lowRISC/ethernet/tree/2dc3a8b12da4006f343d6be82872dd80990cab6f).

What follows is an excessively detailed review of the design part-by-part, largely for the purposes of my own reflection.

# Top-level
![Top-level block diagram](/assets/2026-07-31-ethernet-block-diagram.svg){: width="100%" }

The Ethernet top-level exposes four interfaces:
* A simple memory interface for arbitrary address access
* An RGMII interface to connect to an off-chip PHY
* An MDIO interface, also to connect to the PHY
* An IRQ line

This 'core' top-level can also be wrapped into `axi_top`, which simple translates an AXI4 bus to replace the memory interface.

The top is broadly divided into six blocks:

* A memory map for routing incoming memory transactions to one of four memory regions
* An RX framer
* A TX framer
* CSR's and IRQ's block
* A MAC, which I did not design
* A small loopback module

> An important note about AXI Stream: it is not really anything like AXI. It is not addressable, not pipelined, and really quite simple. Do not see "AXIS" and think "lightweight version of AXI", instead think "some data packed with a valid signal".

## RX is hard
Something I had not anticipated when the project began but became apparently quite early on: RX is far, far more complicated than TX.

For TX, I supposed all I would need is a memory buffer, and a counter to read out of the buffer byte-by-byte until we reached the end of the frame.

Similarly, the RX only needs to receive a stream of bytes over AXI-Stream and

TX, indeed, was very straightforward. RX on the other hand unfolded into a hideously complicated "packeting ring buffer".

To encourage code reuse, I made an effort to decouple the RX buffers from the specifics of the Ethernet protocol. To this end, I designed an `axis_pkt_ring_buffer` ("AXI Stream packet ring buffer"). This is a pretty complex block with a lot of features:

* A single large ring buffer for storing incoming data
* A second memory for storing metadata about the packets in the ring buffer
    * Pointers to the packet head
    * Length of the packet
    * External metadata sampled from `metadata_i` (in my Ethernet use case, this was used to tag packets as broadcast, multicast, or unicast)
* An `abandon_pkt_i` signal which, when pulsed, causes the in-progress packet to be abandoned
* A `pop_i` signal which causes the oldest packet in the metadata table to be popped out
* Status flags indicating the fullness of both memory regions

### Random-access FIFO
The metadata table was implemented as a FIFO, which has the convenient effect of the oldest packet always being at index 0. However, I wanted software to be able to 'peek' at future packets without popping the head, so I had to modify our FIFO primitive to support random reads.

This so-called "random-access FIFO" seems to me like it could be quite useful and I was surprised when I couldn't find an existing design anywhere. My design is of course reusable, exposing three main interface:
* push
* pop
* addressable reads

Read are addressed relative to the read pointer, so reading address 1 will always return the second item in the queue, meaning the physical memory layout is hidden from the software. Reading from an address that isn't populated will return an error.

### Pointer Arithmetic
Pointer arithmetic is hard. Implementing a FIFO is already quite tricky, but is at least a sufficiently well-known problem to have widely accepted solutions (e.g. add an extra MSB to the read and write pointers).

Things got trickier with the ring buffer, though. While it still has a write pointer which increments with incoming data, there is a 'free pointer' rather than a read pointer -- this indicates that all data up-to-and-excluding the free pointer is unused.

To complicate matters, in my use case this free pointers has to be hardwired to the head pointer of the oldest packet in the metadata table, meaning it could just by arbitrary amount when a packet is popped.

Lastly, fencepost errors are of course a nightmare in pointer arithmetic.

# On Reusability
I strived to create *reusable* blocks when working on this design, a goal which I think I largely accomplished.

It's true that the top-level blocks are tightly coupled to the Ethernet protocol:
* `ethernet_rx_framing`
* `ethernet_tx_framing`
* `ethernet_mem_map`
* `ethernet_loopback_mux`
* `ethernet_csr`
* `ethernet_mac_wrapper`

However, some of these are thin wrappers around general-purpose blocks:

* `ethernet_rx_framing` is primarily a wrapper around `axis_pkt_ring_buffer` (though also includes `ethernet_mac_filter`)
* `ethernet_mem_map` is a thin wrapper around `bus`
* `ethernet_loopback_mux` is a thin wrapper around `axis_pkt_mux`

I'm a big fan of this design pattern -- it allows reusable blocks to be integrated rapidly, while keeping the messy business of renaming signals to match the design away from the top-level.

Going further, you'll find I implemented a lot of blocks are being explicitly decoupled from this design:

* `mem_to_ro_mem` -- has two memory interface (upstream and downstream) and simply rejects any write transactions
* `mem_to_wo_mem` -- similar
* `ram_upsizer_w8_r64` -- a RAM primitive with heterogenous widths. Admittedly having the specific bitwidths hardcoded is not the most re-use friendly, but I'd had a lot of struggles battling with messy memory primitives and wasn't going to complicate it even more by parametrising that
* `ram_downsizer_w64_r8` -- similar
* `random_access_fifo` -- discussed elsewhere
* `pkt_wr_ptr_logic` -- discussed elsewhere
* `axis_pkt_isolate`

# Some Elegant Designs
## Loopback Multiplexor
Loopback seemed at first like an easy feature to throw in -- MUX the RX path with two inputs: the true RX, and the TX loopback.

Originally it was just that. On the RGMII interface, after the MAC, I connected them back. I was concerned that packets could be corrupted if the loopback switched mode mid-packet, but placing the MUX before the MAC meant that the frame-check sequence would still be present, and would obviously fail for any corrupted packets. Perfect!

Then came synthesis, and I realised that connected a MUX on the RGMII interface was a major no-no: the RGMII interface includes a clock for the RX data, and FPGA's really do not like you putting a MUX on a clock.

Okay, true I could probably have worked with that, there are clock MUX primitives available on Xilinx FPGA's, but I decided it would be cleaner and simpler just to move the loopback to the AXI Stream, before the MAC.

This was fine, at first, until I realised my loopback test had regressed: the AXI Stream doesn't include the frame check sequence, it's already been removed by the MAC, so any spliced or incomplete frames will get forwarded through to the RX and exposed to the core!

My solution, I thought, was quite elegant. A packet-aware AXI Stream multiplexor.
TODO show that diagram of the feedback paths!

## `pkt_wr_ptr_logic`
A very simple but, in my opinion, elegant design. When designing the `axis_pkt_ring_buffer`, I found the write pointer logic growing just slightly too complicated to keep in the same module.

`pkt_wr_ptr_logic` has a minimal interface:
```verilog
axis_pkt_ring_buffer_wr_ptr_logic #(
    .PTR_W      ()
) inst_name (
    .clk_i      (),
    .rst_ni     (),
    .valid_i    (),
    .commit_i   (),
    .abandon_i  (),
    .wr_ptr_o   (),
    .head_ptr_o ()
);
```

The logic is simple: assert `valid_i` to increment the pointer, normally.
At the end of a packet, assert `commit_i` as well.
If you want to drop the packet, assert `abandon_i`, and it will revert to the start of the current packet.

This will calcualte the appropriate location for the write pointer, as well as exposing a pointer to the head of the current packet (which is what we write to the packet table).

This design is not that impressive -- in fact my verbal description of it is probably longer than it's implementation in SystemVerilog -- but I'm quite proud of the *abstraction*. It keeps the business of incrementing and reverting the pointer away from the top-level, exposing simple transactional concepts instead: commit the packet, abandon the packet.

# On CSR's
The CSR block of this design... is a bit of a mess. It works and I'm confident it will always work, but the code is hard to read and harder to maintain.

This, unfortuanetly, seems to be a universal truth with register blocks. When working at AMD I put significant effort into automating register block generation from a spec, and learned the hard way that register block code is always just a bit... messy. For auto-generated code, this is not necessarily a problem, but it feels like something that ought to have a clean, elegant, widely-acceepted solution, but for some reason... it doesn't.

I think the problem lies in the fact that any clean, elegant abstraction or template will necessarily take away some flexibility, and flexibility is really quite necessary. You need weird exotic registers with side effects on both reads and writes, aliases to other registers, volatility, status registers that read straight from a wire. It's messy.

I've tried to come up with a generalised description of all of these use cases -- first as a number of 'attributes' a register may have, then as a flat list of 'types 'of registers -- and found there are simply too many overlapping requirements.

One solution which I consider *reasonably* elegant is to limit the scope of your register block purely to address decoding and protocol handling. That mean that any configuration flops are implemented elsewhere. In this design, you would expose FOR EACH REGISTER a 'write_en', 'read_en', 'wdata', 'rdata', and similar such signals.

But this is cumbersome - every flop needs to be implemented externally instead. Granted, you should be testing your register blocks, and any blocks not conforming to the register spec will be caught quickly, but it still feels like duplication of effort.
