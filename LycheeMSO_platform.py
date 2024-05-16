#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Ammar Seliaman <me@ammar.engineer>
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk27",  0, Pins("H11"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("T13")), # CARD1:1
        Subsignal("tx", Pins("M11")), # CARD1:11
        # Subsignal("tx", Pins("A7")), # CARD1:1
        # Subsignal("rx", Pins("A6")), # CARD1:11
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("M9"),  IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R10"), IOStandard("LVCMOS33")),
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("N10")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("cs_n", Pins("N11")),
        Subsignal("miso", Pins("M8")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("M8 M7 M10 N11")),
        Subsignal("cmd",  Pins("R14")),
        Subsignal("clk",  Pins("N10")),
        Subsignal("cd",   Pins("D15")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM IMD128M16R39CG8GNF-125.
    ("ddram", 0,
        Subsignal("a", Pins("F7 A4 D6 F8 C4 E6 B1 D8 A5 F9 K3 B7 A3 C8"),
            IOStandard("SSTL15")),
        Subsignal("ba", Pins("H4 D3 H5"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("R4"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("R6"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L2"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("P5"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("G1 K5"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "G5 F5 F4 F3 E2 C1 E1 B3",
            "M3 K4 N2 L1 P4 H3 R1 M2"),
            IOStandard("SSTL15"),
            Misc("VREF=INTERNAL")),
        Subsignal("dqs_p", Pins("G2 J5"), IOStandard("SSTL15D")),
        Subsignal("dqs_n", Pins("G3 K6"), IOStandard("SSTL15D")),
        Subsignal("clk_p", Pins("J1"), IOStandard("SSTL15D")),
        Subsignal("clk_n", Pins("J3"), IOStandard("SSTL15D")),
        Subsignal("cke",   Pins("J2"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("R3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("B9"), IOStandard("SSTL15")),
    ),
]

# Dock 204 Pins SODIMM Connector -------------------------------------------------------------------

_connectors = [
    ["CARD1",
        # A.
        # -------------------------------------------------
        "---", # 0
        #     GND GND  5V  5V  5V  5V GND GND  NC   ( 1-10).
        " T13 --- --- --- --- --- --- --- --- ---",
        #      NC GND GND      NC  NC  NC GND GND   (11-20).
        " M11 --- --- --- T10 --- --- --- --- ---",
        #  NC 3V3  NC 3V3 GND GND                   (21-30).
        " --- --- --- --- --- ---  T6 R16  P6 P15",
        # GND GND                 GND GND           (31-40).
        " --- ---  T7 P16  R8 N15 --- ---  T8  N16",
        #         GND                 GND GND       (41-50).
        "  M6 N14 --- L16  T9 L14  P9 --- --- K15",
        #             GND GND                 GND   (51-60).
        " P11 K14 T11 --- --- K16 R11 J15 T12 ---",
        # GND                 GND                   (61-70).
        " --- H16 R12 H14 P13 --- R13 G16 T14 H15",
        # GND GND                                   (71-72).
        " --- ---",
        # B.
        # -------------------------------------------------
        #                                      NC   (73-82).
        " M15 L13 M14 K11 F13 K12 G12 K13 T15 ---",
        #                  NC  NC                   (83-92).
        " J16 H13 J14 J12 --- --- G14 H12 G15 G11",
        #  NC  NC                  NC  NC      NC  (93-102).
        " --- --- F14 B10 F16 A13 --- --- E15 ---",
        #      NC  NC  NC      NC      NC  NC  NC  (103-112).
        " D15 --- --- --- A15 --- B14 --- --- ---",
        #      NC      NC  NC  NC      NC      NC  (113-122).
        " A14 --- B13 --- --- --- C12 --- B12 ---",
        #      NC      NC GND GND                  (123-132).
        " A12 --- C11 --- --- --- B11 E16 A11 F15",
        # GND GND          NC GND GND      NC      (133-142).
        " --- --- C10 C13 --- --- --- D16 --- E14",
        #     GND GND                 GND GND      (143-152).
        "  B8 --- ---  C9  C6  A9  A7 --- --- L12",
        #         GND GBD                 GND GND  (153-162).
        "  A6 J11 --- ---  C7  E9  D7  E8 --- ---",
        #     VCC     VCC GND GND     VCC     GND  (163-172).
        "  T2 ---  T3 --- --- ---  T4 ---  T5 ---",
        # GND VCC             GND GND              (173-182).
        " --- ---  N6 F10  N7 --- --- D11  N9 D10",
        #     GND GND      NC  NC GND GND          (183-192).
        "  R9 --- --- E10 --- --- --- ---  N8 R7",
        #         GND GND  NC      NC      NC  NC  (193-202).
        "  L9  P7 --- --- ---  M6 ---  L8 --- ---",
        #  NC  NC                                  (203-204).
        " --- ---",
    ],
]

# Dock IOs -----------------------------------------------------------------------------------------

_dock_io = [
    # Function Generator
    # WARN  (CT1122) : 'fGen0' will be placed to RECONFIGN pin according to constraint, and then the signal may lead to gwCONFIG programming directly
    # ("fGen", 0,  Pins( "B10"), IOStandard("LVCMOS33")),
    # ("fGen", 1,  Pins( "A13"), IOStandard("LVCMOS33")), # fpga READY 
    ("fGen", 2,  Pins( "F15"), IOStandard("LVCMOS33")), 
    ("fGen", 3,  Pins( "E15"), IOStandard("LVCMOS33")),
    # ("fGen", 4,  Pins( "C13"), IOStandard("LVCMOS33")), # FPGA DONE
    ("fGen", 5,  Pins("D16"), IOStandard("LVCMOS33")),
    ("fGen", 6,  Pins("E14"), IOStandard("LVCMOS33")),
    ("fGen", 7,  Pins("C9"), IOStandard("LVCMOS33")),
    ("fGen", 8,  Pins("H14"), IOStandard("LVCMOS33")),
    ("fGen", 9,  Pins("G16"), IOStandard("LVCMOS33")),
    ("fGen", 10,  Pins("A9"), IOStandard("LVCMOS33")),

    # Logic Analyzer
    # ("logicAnalyzer", 0,  Pins( "T13"), IOStandard("LVCMOS33")),
    # ("logicAnalyzer", 1,  Pins( "T10"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 2,  Pins( "T7"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 3,  Pins( "R8"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 4,  Pins( "M6"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 5,  Pins( "P9"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 6,  Pins( "T11"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 7,  Pins( "T12"), IOStandard("LVCMOS33")),
    # ("logicAnalyzer", 8,  Pins( "M11"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 9,  Pins( "T6"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 10,  Pins( "P6"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 11,  Pins( "T8"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 12,  Pins( "T9"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 13,  Pins( "P11"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 14,  Pins( "R11"), IOStandard("LVCMOS33")),
    ("logicAnalyzer", 15,  Pins( "H15"), IOStandard("LVCMOS33")),

    ("led", 0,  Pins( "CARD1:44"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 1,  Pins( "CARD1:46"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 3,  Pins( "CARD1:40"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 2,  Pins( "CARD1:42"), IOStandard("LVCMOS18")), # CHECKME: Should be LVCMOS33.
    ("led", 4,  Pins( "CARD1:98"), IOStandard("LVCMOS33")),
    ("led", 5,  Pins("CARD1:136"), IOStandard("LVCMOS33")),

    # Arbitrary Wavefrom Generator
    ("AWG", 0,
     Subsignal("data_0", Pins("L12")),
     Subsignal("data_1", Pins("J11")),
     Subsignal("data_2", Pins("N6")),
     Subsignal("data_3", Pins("N7")),
     Subsignal("data_4", Pins("N9")),
     Subsignal("data_5", Pins("R9")),
     Subsignal("data_6", Pins("D11")),
     Subsignal("data_7", Pins("D10")),
     Subsignal("data_8", Pins("N8")),
     Subsignal("data_9", Pins("L9")),
     Subsignal("data_10", Pins("R7")),
     Subsignal("data_11", Pins("P7")),
     Subsignal("data_12", Pins("M7")),
     Subsignal("data_13", Pins("L8")),

     Subsignal("clk", Pins("E10")),
     Misc("PULL_MODE=NONE"),
     ),

    # RGB Led.
    ("rgb_led", 0, Pins("CARD1:45"), IOStandard("LVCMOS18")),

    # Buttons.
    ("btn_n", 0,  Pins( "CARD1:15"), IOStandard("LVCMOS33")),
    ("btn_n", 1,  Pins("CARD1:165"), IOStandard("LVCMOS15")),
    ("btn_n", 2,  Pins("CARD1:163"), IOStandard("LVCMOS15")),
    ("btn_n", 3,  Pins("CARD1:159"), IOStandard("LVCMOS15")),
    ("btn_n", 4,  Pins("CARD1:157"), IOStandard("LVCMOS15")),

    # HDMI.
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("CARD1:68")),
        Subsignal("clk_n",   Pins("CARD1:70")),
        Subsignal("data0_p", Pins("CARD1:64")),
        Subsignal("data0_n", Pins("CARD1:62")),
        Subsignal("data1_p", Pins("CARD1:58")),
        Subsignal("data1_n", Pins("CARD1:56")),
        Subsignal("data2_p", Pins("CARD1:52")),
        Subsignal("data2_n", Pins("CARD1:50")),
        Subsignal("hdp", Pins("CARD1:154"), IOStandard("LVCMOS18")),
        Subsignal("cec", Pins("CARD1:152"), IOStandard("LVCMOS18")),
        Subsignal("sda", Pins("CARD1:95"),  IOStandard("LVCMOS18")),
        Subsignal("scl", Pins("CARD1:97"),  IOStandard("LVCMOS18")),
        Misc("PULL_MODE=NONE"),
    ),

    # LCD.
    ("lcd", 0,
        # Control.
        Subsignal("rst",   Pins("CARD1:123")),
        Subsignal("bl",    Pins("CARD1:186")),
        Subsignal("sda",   Pins("CARD1: 95")),
        Subsignal("scl",   Pins("CARD1: 97")),
        Subsignal("int",   Pins("CARD1:125")),

        # Video.
        Subsignal("clk",   Pins("CARD1:183")),
        Subsignal("de",    Pins("CARD1:101")),
        Subsignal("hsync", Pins("CARD1:107")),
        Subsignal("vsync", Pins("CARD1:103")),
        Subsignal("r",     Pins("CARD1:193 CARD1:191 CARD1:181 CARD1:177 CARD1:175")),
        Subsignal("g",     Pins("CARD1:180 CARD1:131 CARD1:129 CARD1:194 CARD1:192 CARD1:182")),
        Subsignal("b",     Pins("CARD1:121 CARD1:119 CARD1:115 CARD1:113 CARD1:109")),
        IOStandard("LVCMOS18")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, dock="standard", toolchain="gowin"):

        GowinPlatform.__init__(self, "GW2A-LV18PG256C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2A-18C")
        self.add_extension(_dock_io if dock == "standard" else _dock_lite_io)
        if dock == "lite":
            self.add_connector(_dock_lite_connectors)

        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_jtag_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        # return OpenFPGALoader(cable="ft2232")
        return OpenFPGALoader(cable="ft232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)
