---
title: SystemVerilog is a Terrible Language
layout: post
---

Since I began using it, SystemVerilog has seemed to me like a language with serious limitations. In my second year of college, using it for the first time, I thought surely this only seemed the case because of my inexperience -- I felt quite wise for arriving at this conclusion. Now, several years later, I am inclined to say my first instinct was right. I have been maintaining a list of nits I have with SystemVerilog.

Granted most of these gripes are focused on the syntax of the language rather than the underlying structures -- really, this is because SystemVerilog is only a syntax, and any issue I take with the underlying capabilities it offers would be an issue with digital electronics as a discipline.

Some of these notes are also criticisms of how the language is _normally used_, which is not necessarily fair to those who wrote the standard.

Given the sheer amount of time I spend working with this language, you can expect this list to grow in future!

## No disambiguation of inputs and outputs
Take an example like the below:
```verilog
module eth_mac_1g_rgmii (
    input  clk,
    input  rst_n,
    // whatever signals you may have
    output rx_clk
);
    rgmii_phy_if (
        // whatever
        .clk    (clk),
        .rx_clk (rx_clk)
    );

    eth_mac_1g (
        // whatever
        .clk    (clk),
        .rx_clk (rx_clk)
    );
endmodule
```
Suppose I'm tracing the `rx_clk` signal and I arrive here -- is it driven by `rgmii_phy_if` or `eth_mac_1g`? I suppose I'll have to open both and check. Repeat at every level of hierarchy.

Of course, there is a relatively widespread convention (for example in [the lowRISC style guide](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md)) of suffixing ports with `_o` and `_i` to disambiguate, which helps enormously. But having spent many hours debugging legacy code that _didn't_ adhere to this convention, I feel it's a failing of the language itself not to save poor junior engineers from this fate.

## Instantiations do not resemble declarations
Languages like C have the wonderful feature that the syntax for *calling* a function greatly resembles the syntax for declaring one. So, you see a function declared like this:
```C
void ethernet_intr_mask_set(ethernet_t ethernet, ethernet_intr intr_mask);
```
Well, if you want to call it, simply copy-paste the line, remove the `void`, and substitue your arguments:
```C
ethernet_intr_mask_set(my_ethernet, 0);
```

In SystemVerilog, instantiated a module doesn't offer the same convenience:
```verilog
// Declaring a module looks like this:
module my_axi_device (
    // Clocking and reset
    input  logic clk_i,
    input  logic rst_ni,

    // AXI device interface
    input  axi_req_t axi_req_i,
    output axi_rsp_t axi_rsp_o
);

// Instantiating one looks like this:
my_axi_device my_instance_name (
    .clk_i      ( /*placeholder*/ ),
    .rst_ni     ( /*placeholder*/ ),
    .axi_req_i  ( /*placeholder*/ ),
    .axi_rsp_O  ( /*placeholder*/ )
);
```
I've often wondered (while tediously converting the former to the latter, revelling in how clever I am using the multiline editor to replace 'input's with '.'s, then realising I'd included a blank line or comment in my multiline cursor and have royally screwed up the formatting and need to begin again) if a high-end IDE couldn't automate this process for me. At the time of writing I don't have access to any such tool, so I put together my own quick-and-dirty script for it (which I may share, if I find time to clean it up).

## No way of setting required parameters
I think this title speaks for itself -- most EDA tools (though not all) require module parameters to have a default value assigned to them, essentially making them optional.

The problem, of course, being that plenty of modules do not have a 'sensible default' configuration. What is the 'default' memory for a RAM primitive, for instance?

## The `end` of the `begin`ing
Hopefully another title that speaks for itself -- though supposedly inspired by C, SystemVerilog, for some unknowable reason prefers keywords `begin` and `end` to the simple \{curly braces\} preferred by languages such as C and by developers such as everybody.

This is a lovely surprise when, for whatever reason, one finds oneself working without their preferred IDE, in something like pluginless Vim, where most syntax highlighters will not highlight matching `begin`/`end` pairs, leaving you at the mercy of the original author's indentation.

That manifests at its worst when a software engineer with a delusion of understanding SystemVerilog writes an `always_comb` block spanning hundreds of lines, driving multiple FSMs, and creating an abundance of inferred latches to add to the ever-growing list of "oh don't worry about that one, it's always there" warnings.

## Attributes are underused
I have seen RTL which provides meta-information to PD teams using the _names_ of signals, with rules like:

- If `clk` appears at the start or end of the signal name, it is a clock for STA purposes
- If `seu` appears in the signal name, it should be SEU-hardened

It seems to me this is exactly the use case for _attributes_, which offer a far more robust approach to this than fragile naming conventions. The advantage of naming, I suppose, is that it is guaranteed to be supported by all views in all tooling.

I see potential for far more powerful applications of attributes:

- Mark nets as false paths inline, rather than in a separate constraints file where it can break if the signal name ever changes or the file moves
- Provide hints for synthesis tools about expected switching activity on a net

## Verbosity
I do appreciate the Zen of Python's second argument: Explicit is better than implicit.

Nonetheless, I shudder to imagine the accumulated wear-and-tear on my keyboard from the sheer number of times I have typed the **exact** string `always_ff @ (posedge clk_i or negedge rst_ni) begin`.

I don't really have a better idea in mind (don't say macros) but it certainly warrants an analysis.

## Interfaces are underutilised
It seems historically there was mixed supported among EDA vendors for SystemVerilog `interface`s, which is often pointed to as the reason not to use them.

As far as I can tell, they are now supported by all major EDA tools (though I am open to being corrected if you know of any exceptions).

I strongly suspect the real reason interfaces are not adopted by many teams is simply because they confuse people -- certainly they confused me -- who assume initially that they would behave like a `struct`, but bidirectional. In fact, interfaces are conceptually closer to modules than structs, and once one takes the time to understand them, their usefulness is irrefutable.

To me, the key advantage of interfaces over structs is not any of the fancy `clocking` or `modports` -- it is simply the fact that they are _parametrisable_.

Perhaps you can relate -- suppose your SoC has a 64-bit address space, so you've defined a bus `struct` with a 64-bit address wire. Now suppose some peripheral only uses 10 bits of address space. On first lint, your terminal is flooded with a deluge of 54 "UNUSEDSIGNAL"s. If only you could parametrise the width of the address.
