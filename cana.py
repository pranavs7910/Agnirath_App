import struct

# Dictionary generated from your DBC file content
DBC = {
    0x403: {"name": "MC_Velocity", "signals": [
        {"name": "Motor_Velocity",   "start": 0,  "len": 32, "scale": 1, "offset": 0, "unit": "RPM", "float32": True},
        {"name": "Vehicle_Velocity", "start": 32, "len": 32, "scale": 1, "offset": 0, "unit": "m/s", "float32": True},
    ]},
    0x601: {"name": "CMU_1_Data_1", "signals": [
        {"name": "CMU_1_SlNo",  "start": 0,  "len": 32, "scale": 1,   "offset": 0, "unit": ""},
        {"name": "PCB_1_Temp",  "start": 32, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
        {"name": "Cell_1_Temp", "start": 48, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
    ]},
    0x604: {"name": "CMU_4_Data_1", "signals": [
        {"name": "CMU_4_SlNo",  "start": 0,  "len": 32, "scale": 1,   "offset": 0, "unit": ""},
        {"name": "PCB_4_Temp",  "start": 32, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
        {"name": "Cell_4_Temp", "start": 48, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
    ]},
    0x605: {"name": "CMU_5_Data_1", "signals": [
        {"name": "CMU_5_SlNo",  "start": 0,  "len": 32, "scale": 1,   "offset": 0, "unit": ""},
        {"name": "PCB_5_Temp",  "start": 32, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
        {"name": "Cell_5_Temp", "start": 48, "len": 16, "scale": 0.1, "offset": 0, "unit": "C"},
    ]},
    0x6F6: {"name": "PreCharge_Status", "signals": [
        {"name": "Precharge_Contactor_Driver_Stat", "start": 0,  "len": 8, "scale": 1, "offset": 0, "unit": ""},
        {"name": "Precharge_State",                 "start": 8,  "len": 8, "scale": 1, "offset": 0, "unit": ""},
        {"name": "Precharge_Timer_Elapsed",         "start": 48, "len": 8, "scale": 1, "offset": 0, "unit": ""},
        {"name": "Precharge_Timer",                 "start": 56, "len": 8, "scale": 1, "offset": 10, "unit": "ms"},
    ]},
    0x6F8: {"name": "BMS_Error_Flags", "signals": [
        {"name": "Cell_Over_Voltage",        "start": 32, "len": 1, "scale": 1, "offset": 0, "unit": ""},
        {"name": "Cell_Under_Voltage",       "start": 33, "len": 1, "scale": 1, "offset": 0, "unit": ""},
        {"name": "Cell_Over_Temp",           "start": 34, "len": 1, "scale": 1, "offset": 0, "unit": ""},
        {"name": "CMU_Comms_Timeout",        "start": 36, "len": 1, "scale": 1, "offset": 0, "unit": ""},
    ]},
    0x6FA: {"name": "Battery_Volt_Current", "signals": [
        {"name": "Battery_Voltage", "start": 0,  "len": 32, "scale": 1, "offset": 0, "unit": "mV"},
        {"name": "Battery_Current", "start": 32, "len": 32, "scale": 1, "offset": 0, "unit": "mA"},
    ]},
}

RAW_DATA = """456071	0x6F8	8	65 0E BA 0F 01 02 02 07
456071	0x6FA	8	B2 07 00 00 54 23 00 00
456072	0x6F6	8	AD 00 1E FB 5F FB 01 00
456094	0x604	8	8F 0E 00 00 09 01 70 FE
456096	0x601	8	96 12 00 00 0B 01 70 FE"""

def extract_bits_le(data, start_bit, bit_len):
    """Refined version: Extracts bits for Intel/Little Endian format."""
    full_int = int.from_bytes(data, 'little')
    mask = (1 << bit_len) - 1
    return (full_int >> start_bit) & mask

def decode_frame(can_id, data):
    msg_def = DBC.get(can_id)
    if not msg_def:
        return None
    
    decoded_signals = []
    for sig in msg_def["signals"]:
        raw = extract_bits_le(data, sig["start"], sig["len"])
        
        # Handle Float32 if specified
        if sig.get("float32"):
            # Use native/little endian unpack
            raw = struct.unpack('<f', struct.pack('<I', raw))[0]
            
        value = (raw * sig["scale"]) + sig["offset"]
        decoded_signals.append(f"    {sig['name']}: {value:.2f} {sig['unit']}")
        
    return {"name": msg_def["name"], "signals": decoded_signals}

def run_decoder():
    print(f"{'TIMESTAMP':<10} | {'CAN ID':<8} | {'MESSAGE NAME'}")
    print("-" * 50)
    
    for line in RAW_DATA.strip().split("\n"):
        parts = line.split("\t")
        ts = parts[0]
        can_id = int(parts[1], 16)
        payload = bytes(int(b, 16) for b in parts[3].split())
        
        result = decode_frame(can_id, payload)
        if result:
            print(f"{ts:<10} | 0x{can_id:03X}   | {result['name']}")
            for s in result['signals']:
                print(s)
        else:
            print(f"{ts:<10} | 0x{can_id:03X}   | [Unknown ID]")
        print()

if __name__ == "__main__":
    run_decoder()