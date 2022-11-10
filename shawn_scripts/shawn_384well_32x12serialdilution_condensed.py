from opentrons import protocol_api
import time
import sys


metadata = {
    'protocolName': '384 well plate, 32x12 1:1 Serial Dilution',
    'author': 'Shawn Laursen',
    'description': '''This protocol will make 32x12well dilutions in a 384 well
                      plate. The dilutions are 1:1 across the the plate and
                      leave the last well of each dilution with buffer (DNA)
                      only. It will take the even columns of a 96 well plate to
                      fill well 1 of each dilution and the adjacent well in the
                      96 well plate will provide the dilution buffer for the
                      other 11 wells of each dilution.''',
    'apiLevel': '2.8'
    }

    #setup
    tips300 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips20 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    plate96 = protocol.load_labware('costar_96_wellplate_200ul', 2)
    plate384 = protocol.load_labware('corning3575_384well_alt', 5)
    p300m = protocol.load_instrument('p300_multi_gen2', 'left',
                                     tip_racks=[tips300])
    p20m = protocol.load_instrument('p20_multi_gen2', 'right',
                                     tip_racks=[tips20])

def run(protocol: protocol_api.ProtocolContext):
    #turn on robot rail lights
    strobe(5)

    #do titration
    titrate(1, 0, 0, 'odd')
    test_titrate(3, 2, 0, 'even')
    #titrate(5, 4, 12, 'odd')
    #titrate(7, 6, 12, 'even')

    #turn off robot rail lights
    strobe(5)
    protocol.set_rail_lights(False)

def strobe(blinks):
    i = 0
    while i < blinks:
        protocol.set_rail_lights(True)
        time.sleep(0.25)
        protocol.set_rail_lights(False)
        time.sleep(0.25)
        i += 1
    protocol.set_rail_lights(True)

def titrate(buff_96col, protien_96col, start_384well, which_rows):
    if which_rows == 'odd':
        which_rows = 0
    elif which_rows == 'even':
        which_rows = 1
    else:
        sys.exit('Wrong value for which_rows.')

    p300m.flow_rate.aspirate = 5
    p300m.flow_rate.dispense = 10
    p20m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][buff_96col].bottom(1.75),
                     plate384.rows()[which_rows][(start_384well+1):(start_384well+12)],
                     disposal_volume=5, new_tip='never')
    p300m.flow_rate.dispense = 5
    p300m.transfer(40, plate96.rows()[0][protien_96col].bottom(1.75),
                   plate384.rows()[0][0])
    p300m.drop_tip()
    p20m.pick_up_tip()
    p20m.transfer(20, plate384.rows()[which_rows][start_384well:(start_384well+10)],
                  plate384.rows()[which_rows][(start_384well+1):(start_384well+11)],
                  mix_after=(3, 20), new_tip='never')
    p20m.aspirate(20, plate384.rows()[which_rows][(start_384well+10)])
    p20m.drop_tip()

def test_titrate(buff_96col, protien_96col, start_384well, which_rows):
    if which_rows == 'odd':
        which_rows = 0
    elif which_rows == 'even':
        which_rows = 1
    else:
        sys.exit('Wrong value for which_rows.')

    p300m.flow_rate.aspirate = 5
    p300m.flow_rate.dispense = 10
    p20m.pick_up_tip()
    p300m.distribute(20, plate96.rows()[0][buff_96col].bottom(1.75),
                     plate384.rows()[which_rows][(start_384well+1):(start_384well+12)],
                     disposal_volume=5, new_tip='never')
    p300m.flow_rate.dispense = 5
    p300m.transfer(40, plate96.rows()[0][protien_96col].bottom(1.75),
                   plate384.rows()[0][0])
    p300m.transfer(20, plate384.rows()[which_rows][start_384well:(start_384well+10)],
                  plate384.rows()[which_rows][(start_384well+1):(start_384well+11)],
                  mix_after=(3, 20), new_tip='never')
    p300m.aspirate(20, plate384.rows()[which_rows][(start_384well+10)])
    p300m.drop_tip()
