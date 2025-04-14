'''
Apply a battery profile after optimization to the batteries
'''

def apply_profile_battery(optimization_result,controller):
    for bat in range(len(controller.get_registered_devices()['batteries'])):
        controller.get_registered_devices()['batteries'][bat].profile = (optimization_result["battery_discharge"][bat] - optimization_result["battery_charge"][bat]) / controller.get_registered_devices()['batteries'][bat].p_bess
        controller.get_registered_devices()['batteries'][bat].soc_profile = optimization_result["battery_soc"][bat]