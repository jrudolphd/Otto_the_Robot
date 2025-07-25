from opentrons import protocol_api
import time

metadata = {
    'protocolName': '5cmpd PARPi HPLC Assay pt.1',
    'author': 'Thomas Stilley',
    'description': '''HPLC
                    Tips:
                    p300 5 for Buffers, NAD, 2toMix, Quench
                    p20 1 for CMPD addition
                    - Prepare Pre-mixes
                        Buffer
                        P18
                        PARP1
                        +/- HPF1
                    - Quench Solution
                        1M Perchloric Acid
                   
                    Robot
                    - Transfer 80uL Premix to all wells

                    - Transfer 1uL Inhibitor to all wells
                    - Mix (3x60)

                    - Initiate reaction w 20uL NAD in all wells

                    - Each rxn runs for 8min
                    - Distribute 95uL Quench after 8min
                    STOP and Centrifuge''',
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
  
    parameters.add_int(
        variable_name="RXN_time",
        display_name="P1 RXN time",
        description="Reaction duration for PARP1 reaction.",
        default=8,
        minimum=0,
        maximum=1000,
        unit="min"
    )
    parameters.add_int(
        variable_name="CMPD_Half",
        display_name="Half w/ CMPDs",
        description="Which Set of CMPDs in plate. 1-2",
        default=1,
        minimum=1,
        maximum=2,
        unit="half"
    )

def run(protocol):
    # set variables

    start_96well = protocol.params.start_96well - 1
    RXN_time = protocol.params.RXN_time
    CMPD_Half = protocol.params.CMPD_Half

    # run protocol
    strobe(12, 8, True, protocol)
    setup(protocol)
    p300m.pick_up_tip()
    HPLC(start_96well, RXN_time, CMPD_Half, protocol)
    p300m.drop_tip()
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
    global tips300, p20m, p300m, plate96, trough, cmpd_plate
    
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    tips300b = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 9)
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300, tips300b])
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 3)
    trough = protocol.load_labware('nest_12_reservoir_15mL', 2)
    cmpd_plate = protocol.load_labware('costar_96_wellplate_200ul', 6)


def HPLC(start_96well,  RXN_time, CMPD_Half, protocol):
    # Reagents
    Buffer_noHPF1 = trough.wells_by_name()['A1']
    Buffer_HPF1 = trough.wells_by_name()['A2']
    NAD = trough.wells_by_name()['A3']
    QuenchSol = trough.wells_by_name()['A4']
    NaOAc = trough.wells_by_name()['A5']
    KOH = trough.wells_by_name()['A6']

    # Num pairs
    rows_noHPF1 = slice(0,6)
    rows_HPF1 = slice(6,12)

    # add premixes
    p300m.distribute(80, Buffer_noHPF1, plate96.rows()[0][rows_noHPF1], new_tip='never')
    p300m.drop_tip()

    p300m.pick_up_tip()
    p300m.distribute(80, Buffer_HPF1, plate96.rows()[0][rows_HPF1], new_tip='never')
    p300m.drop_tip()

    
    # add inhibitors
    if CMPD_Half == 1:
        cmpd1 = 0
        cmpd2 = 1
        cmpd3 = 2
        cmpd4 = 3
        cmpd5 = 4
        control = 5
    if CMPD_Half == 2:
        cmpd1 = 6
        cmpd2 = 7
        cmpd3 = 8
        cmpd4 = 9
        cmpd5 = 10
        control = 11
   

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd1], plate96.rows()[0][0], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd1], plate96.rows()[0][6], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd2], plate96.rows()[0][1], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd2], plate96.rows()[0][7], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd3], plate96.rows()[0][2], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd3], plate96.rows()[0][8], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd4], plate96.rows()[0][3], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd4], plate96.rows()[0][9], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd5], plate96.rows()[0][4], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][cmpd5], plate96.rows()[0][10], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    p20m.pick_up_tip()
    p20m.distribute(1, cmpd_plate.rows()[0][control], plate96.rows()[0][5], disposal_volume = 1, new_tip = 'never')
    p20m.distribute(1, cmpd_plate.rows()[0][control], plate96.rows()[0][11], disposal_volume = 1, new_tip = 'never')
    p20m.drop_tip()

    # Mix
    for i in range(0,12):
        p300m.pick_up_tip()
        p300m.mix(3, 60, plate96.rows()[0][i])
        p300m.drop_tip()

    # initiate w NAD
    p300m.pick_up_tip()
    p300m.distribute(20, NAD, plate96.rows()[0][rows_noHPF1], disposal_volume = 0, new_tip='never')

    p300m.distribute(20, NAD, plate96.rows()[0][rows_HPF1], disposal_volume = 0, new_tip='never')
    p300m.drop_tip()

    # RXN Time
    protocol.delay(minutes=RXN_time)
    
    # Quench
    p300m.pick_up_tip()
    p300m.distribute(95, QuenchSol, plate96.rows()[0][rows_noHPF1], disposal_volume=15, new_tip='never')
    p300m.distribute(95, QuenchSol, plate96.rows()[0][rows_HPF1], disposal_volume=15, new_tip='never')


