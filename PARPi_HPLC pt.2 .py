from opentrons import protocol_api
import time

metadata = {
    'protocolName': '5cmpd PARPi HPLC Assay pt.2',
    'author': 'Thomas Stilley',
    'description': '''HPLC pt.2
                    Tips: 
                    p300 1 per sample column and 2 for NaOAc and KOH
                    
                    - Distribute 13uL NaOAc to 2nd half of plate

                    - Extract 130uL supernatant from spun wells
                    - Transfer to 2nd plate w NaOAc

                    - Distribute 13uL KOH to 2nd plate
                    - Mix with Shaker module or desktop vortex
                    - Precipitate Salt

                

                    -STOP
                    Centrifuge for 5min at 1000rpm''',
    'apiLevel': '2.18'
    }

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="start_96well",
        display_name="96 column start",
        description="Which column to start in. Indexed from 1.",
        default=1,
        minimum=1,
        maximum=12,
        unit="column"
    )

def run(protocol):
    # set variables
    start_96well = protocol.params.start_96well - 1
    
   
    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    shaker.close_labware_latch()
    p300m.pick_up_tip()
    HPLC(start_96well, protocol)
    strobe(12, 8, False, protocol)

def strobe(blinks, hz, leave_on, protocol):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(1/hz)
        protocol.set_rail_lights(False)
        time.sleep(1/hz)
        i += 1
    protocol.set_rail_lights(leave_on)

def setup(protocol):
    # equipment
    global tips300, tips300b, p300m, plate96, trough, newplate96, shaker
    
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    tips300b = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300b])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 3)
    trough = protocol.load_labware('nest_12_reservoir_15mL', 2)
    shaker = protocol.load_module('heaterShakerModuleV1', 10)
    newplate96 = shaker.load_labware('costar_96_wellplate_200ul')


def HPLC(start_96well, protocol):
    # Reagents
    Buffer_noHPF1 = trough.wells_by_name()['A1']
    Buffer_HPF1 = trough.wells_by_name()['A2']
    NAD = trough.wells_by_name()['A3']
    QuenchSol = trough.wells_by_name()['A4']
    NaOAc = trough.wells_by_name()['A5']
    KOH = trough.wells_by_name()['A6']

     # Slice Names
    spun_noHPF1 = slice(0,6)
    spun_HPF1 = slice(6,12)
    rows_noHPF1 = slice(0,6)
    rows_HPF1 = slice(6,12)

    slice1 = slice(0,3)
    slice2 = slice(3,6)
    slice3 = slice(6,9)
    slice4 = slice(9,12)

    # Fill half plate w 1M NaOAc

    p300m.distribute(13, NaOAc, newplate96.rows()[0][rows_noHPF1], disposal_volume = 0, new_tip = 'never')
    p300m.distribute(13, NaOAc, newplate96.rows()[0][rows_HPF1], disposal_volume = 0, new_tip = 'never')

    p300m.drop_tip()
   
    # Pull off supernatant

    p300m.well_bottom_clearance.aspirate = 3
    p300m.flow_rate.aspirate = 45
    p300m.transfer(130, plate96.rows()[0][spun_noHPF1], newplate96.rows()[0][rows_noHPF1], disposal_volume = 0, new_tip = 'always')

    p300m.transfer(130, plate96.rows()[0][spun_HPF1], newplate96.rows()[0][rows_HPF1], disposal_volume= 0, new_tip = 'always')
   
    # Re-neutralization
    
    p300m.well_bottom_clearance.dispense = 3
    p300m.pick_up_tip()
    
    p300m.distribute(13, KOH, newplate96.rows()[0][slice1], disposal_volume = 0, new_tip = 'never')
    shaker.set_and_wait_for_shake_speed(1000)
    protocol.delay(minutes=1)
    shaker.deactivate_shaker()

    p300m.distribute(13, KOH, newplate96.rows()[0][slice2], disposal_volume = 0, new_tip = 'never')
    shaker.set_and_wait_for_shake_speed(1000)
    protocol.delay(minutes=1)
    shaker.deactivate_shaker()

    p300m.distribute(13, KOH, newplate96.rows()[0][slice3], disposal_volume = 0, new_tip = 'never')
    shaker.set_and_wait_for_shake_speed(1000)
    protocol.delay(minutes=1)
    shaker.deactivate_shaker()

    p300m.distribute(13, KOH, newplate96.rows()[0][slice4], disposal_volume = 0, new_tip = 'never')
    shaker.set_and_wait_for_shake_speed(1000)
    protocol.delay(minutes=1)
    shaker.deactivate_shaker()

    p300m.drop_tip()
    shaker.open_labware_latch()

   


   

   

    

