#!/usr/bin/env python3

#
# Copyright (c) 2024 Ammar Seliaman <me@ammar.engineer>
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.soc.integration.soc_core import SoCCore
import LycheeMSO_platform

from litex.soc.doc import generate_docs, generate_svd

from litedram.phy import GW2DDRPHY
from litedram.modules import MT41K64M16

from migen import Signal, ClockDomain
from litex.gen import LiteXModule, Instance, If, Cat
from liteeth.phy.rmii import LiteEthPHYRMII
from litex.soc.integration.builder import Builder

from litex.soc.cores.gpio import GPIOIn, GPIOOut


from litex.soc.cores.clock.gowin_gw2a import GW2APLL
from migen.genlib.resetsync import AsyncResetSynchronizer


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_video_pll=False):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        self.cd_init = ClockDomain()
        self.cd_sys2x = ClockDomain()
        self.cd_sys2x_i = ClockDomain()

        # # #

        self.stop = Signal()
        self.reset = Signal()

        # Clk
        clk27 = platform.request("clk27")

        # Power on reset (the onboard POR is not aware of reprogramming)
        por_count = Signal(16, reset=2**16 - 1)
        por_done = Signal()
        self.comb += self.cd_por.clk.eq(clk27)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys2x_i, 2 * sys_clk_freq)
        self.specials += [
            Instance(
                "DHCEN",
                i_CLKIN=self.cd_sys2x_i.clk,
                i_CE=self.stop,
                o_CLKOUT=self.cd_sys2x.clk,
            ),
            Instance(
                "CLKDIV",
                p_DIV_MODE="2",
                i_CALIB=0,
                i_HCLKIN=self.cd_sys2x.clk,
                i_RESETN=~self.reset,
                o_CLKOUT=self.cd_sys.clk,
            ),
            AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.rst | self.reset),
        ]

        # Init clock domain
        self.comb += self.cd_init.clk.eq(clk27)
        self.comb += self.cd_init.rst.eq(pll.reset)


class BaseSoC(SoCCore):
    def __init__(
        self,
        sys_clk_freq=48e6,
        with_spi_flash=False,
        # with_buttons=True,
        # with_video_terminal=False,
        # with_ethernet=False,
        # with_etherbone=False,
        eth_ip="192.168.1.50",
        # eth_dynamic_ip=False,
        dock="standard",
        **kwargs,
    ):
        platform = LycheeMSO_platform.Platform(dock, toolchain="gowin")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            ident="LiteX SoC on Tang Primer 20K",
            **kwargs,
        )
        # DDR3 SDRAM -------------------------------------------------------------------------------
        self.ddrphy = GW2DDRPHY(
            pads=platform.request("ddram"), sys_clk_freq=sys_clk_freq
        )
        self.ddrphy.settings.rtt_nom = "disabled"
        self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
        self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
        self.add_sdram(
            "sdram",
            phy=self.ddrphy,
            module=MT41K64M16(sys_clk_freq, "1:2"),
            l2_cache_size=kwargs.get("l2_size", 8192),
        )
        # SPI Flash --------------------------------------------------------------------------------
        # from litespi.modules import W25Q32JV as SpiFlashModule
        # from litespi.opcodes import SpiNorFlashOpCodes as Codes

        # self.add_spi_flash(mode="1x", module=SpiFlashModule(Codes.READ_1_1_1))

        # Ethernet / Etherbone ---------------------------------------------------------------------
        # self.ethphy = LiteEthPHYRMII(
        #     clock_pads=self.platform.request("eth_clocks"),
        #     pads=self.platform.request("eth"),
        #     refclk_cd=None,
        # )
        # self.add_etherbone(
        # phy         = self.ethphy,
        # ip_address  = "192.168.1.50",
        # mac_address = 0x10e2d5000001)
        # self.add_csr("ethphy")
        # self.add_ethernet(phy=self.ethphy, dynamic_ip=False, with_timing_constraints=False)
        # self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_timing_constraints=False)

        # LiteScope ---------- ---------------------------------------------------------------------
        from litescope import LiteScopeAnalyzer
        analyzer_signals = [platform.request("btn_n", 0), platform.request("btn_n", 1)]
        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
            depth        = 512,
            clock_domain = "sys",
            samplerate   = sys_clk_freq,
            csr_csv      = "analyzer.csv"
        )

        # UART -------------------------------------------------------------------------------------
        # Already built by SoCCore...

        # Buttons ----------------------------------------------------------------------------------
        self.comb += [
            # WARN  (CT1122) : 'fGen0' will be placed to RECONFIGN pin according to constraint, and then the signal may lead to gwCONFIG programming directly
            # self.platform.request("fGen", 0).eq(0),
            # self.platform.request("fGen", 1).eq(1),
            # self.platform.request("fGen", 2).eq(0),
            # self.platform.request("fGen", 3).eq(0),
            # self.platform.request("fGen", 4).eq(0),
            self.platform.request("fGen", 5).eq(0),
            self.platform.request("fGen", 6).eq(0),
            self.platform.request("fGen", 7).eq(1),
            self.platform.request("fGen", 8).eq(0),
            self.platform.request("fGen", 9).eq(0),
            self.platform.request("fGen", 10).eq(0),


            self.platform.request("logicAnalyzer",2).eq(1), # T7 should be off. It was ON
            self.platform.request("logicAnalyzer",3).eq(0),
            self.platform.request("logicAnalyzer",4).eq(0),
            self.platform.request("logicAnalyzer",5).eq(0),
            self.platform.request("logicAnalyzer",6).eq(0),
            self.platform.request("logicAnalyzer",7).eq(0),
            # self.platform.request("logicAnalyzer",8).eq(0),
            self.platform.request("logicAnalyzer",9).eq(0),
            self.platform.request("logicAnalyzer",10).eq(0),
            self.platform.request("logicAnalyzer",11).eq(0),
            self.platform.request("logicAnalyzer",12).eq(0),
            self.platform.request("logicAnalyzer",13).eq(0),
            self.platform.request("logicAnalyzer",14).eq(0),
            self.platform.request("logicAnalyzer",15).eq(0),
        ]




        # self.submodules.leds = GPIOOut(Cat(*[platform.request("fGen", i) for i in range(11)]))
        # self.add_csr("leds")


# Build --------------------------------------------------------------------------------------------
def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(
        platform=LycheeMSO_platform.Platform,
        description="LycheeMSO + LiteX SoC on Tang Primer 20K.",
    )

    # fmt: off
    parser.add_target_argument("--build-doc", action="store_true", help="Build Documentation")
    parser.add_target_argument("--flash", action="store_true", help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=48e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash", action="store_true", help="Enable SPI Flash (MMAPed).")
    parser.add_argument("--with-etherbone", action="store_true", help="Add EtherBone.")
    parser.add_target_argument("--eth-ip", default="192.168.1.50", help="Etherbone IP address.")
    parser.set_defaults(cpu_type="picorv32")
    parser.set_defaults(cpu_variant="minimal")
    # fmt: on

    args = parser.parse_args()
    if args.build_doc and not args.build:
        print("Use --build with --build-doc")
        exit(1)

    soc = BaseSoC(
        sys_clk_freq=args.sys_clk_freq,
        with_spi_flash=args.with_spi_flash,
        with_etherbone=args.with_etherbone,
        eth_ip=args.eth_ip,
        **parser.soc_argdict,
    )
    builder = Builder(soc, **parser.builder_argdict)
    vns = None
    if args.build:
        builder.csr_csv = "test/csr.csv"
        vns = builder.build(**parser.toolchain_argdict)

    if args.build_doc and args.build:
        soc.do_exit(vns)
        generate_docs(soc, "build/documentation")
        generate_svd(soc, "build/software")

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(
            0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True
        )


if __name__ == "__main__":
    main()
