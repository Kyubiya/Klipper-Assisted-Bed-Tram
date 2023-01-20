#   Assisted Bed Tram
#
#   Klipper module that mimics Marlin's Assisted Bed Tram wizard

class AssistedBedTram:
    def __init__(self, config):
        self.config = config
        self.printer = config.get_printer()

        # Read config
        self.max_diff = config.getfloat('max_diff', 0.05)
        self.horizontal_move_z = config.getfloat('horizontal_move_z', 5.)
        self.speed = config.getfloat('speed', 50., above=0.)

        # Register command
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command("ASSISTED_BED_TRAM",
                                    self.cmd_ASSISTED_BED_TRAM,
                                    desc=self.cmd_ASSISTED_BED_TRAM_help)
    cmd_ASSISTED_BED_TRAM_help = "Marlin style assisted bed tramming"

    def cmd_ASSISTED_BED_TRAM(self, gcmd):
        # Get config objects
        screwstiltadjust = self.printer.lookup_object('screws_tilt_adjust')
        toolhead = self.printer.lookup_object('toolhead')
        reactor = self.printer.get_reactor()
        probe = self.printer.lookup_object('probe')

        curtime = self.printer.get_reactor().monotonic()
        if 'z' not in toolhead.get_status(curtime)['homed_axes']:
            self.gcode.respond_info("Homing...")
            self.gcode.run_script_from_command('G28')

        self.gcode.respond_info("Checking screws...")
        self.gcode.run_script_from_command('SCREWS_TILT_CALCULATE')

        results = []
        # Wait for results
        while True:
            eventtime = reactor.monotonic()
            print_time, est_print_time, lookahead_empty = toolhead.check_busy(eventtime)
            if lookahead_empty:
                    results = screwstiltadjust.get_status(eventtime)
                    break

        results = sorted(results['results'], key=lambda x:x['z'])
        max_z = results[-1]['z']
        self.gcode.respond_info("Max is %.5f" % max_z)
        min_z = results[0]['z']
        self.gcode.respond_info("Min is %.5f" % min_z)
        dif_z = max_z - min_z
        self.gcode.respond_info("Difference is %.5f" % dif_z)

        if dif_z > self.max_diff:
            for screws in results[:-1]:
                cur_dif = max_z - screws['z']
                self.gcode.respond_info("Difference at %s is %.5f" % (screws['name'], cur_dif))
                if cur_dif > self.max_diff:
                    self.gcode.respond_info("Moving to %.2f,%.2f" % (screws['x'], screws['y']))
                    self.gcode.run_script_from_command("G91")
                    self.gcode.run_script_from_command("G1 Z%d" % self.horizontal_move_z)
                    self.gcode.run_script_from_command("G90")
                    self.gcode.run_script_from_command("G1 X%.2f Y%.2f F%d" % (screws['x'], screws['y'], self.speed*60))
                    probe.mcu_probe.lower_probe()
                    self.gcode.run_script_from_command("G1 Z%.5f F%d" % (max_z, self.speed*30))
                    while True:
                        print_time = toolhead.get_last_move_time()
                        triggered = probe.mcu_probe.query_endstop(print_time)
                        if triggered:
                            probe.mcu_probe.raise_probe()
                            probe.mcu_probe.verify_raise_probe()
                            break
                else:
                    self.gcode.respond_info("Within range, skipping %s" % screws['name'])
                self.gcode.respond_info("%s done" % screws['name'])
                self.gcode.run_script_from_command("G4 P100")
        else:
            self.gcode.respond_info("All screws within range")
            
def load_config(config):
    return AssistedBedTram(config)