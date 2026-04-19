#include <iostream>
#include <cstdint>

// DBC Info: 0|32@1+ (1,0)
// 0  = Start Bit
// 32 = Length
// @1 = Little Endian
// +  = Unsigned
// (1,0) = Factor 1, Offset 0

float extract_voltage(const uint8_t* can_data) {
    // 1. Combine the 4 bytes into a single 32-bit unsigned integer
    // Since it's Little Endian, the first byte is the least significant (LSB)
    uint32_t raw_val = ((uint32_t)can_data[0] << 0)  |
                       ((uint32_t)can_data[1] << 8)  |
                       ((uint32_t)can_data[2] << 16) |
                       ((uint32_t)can_data[3] << 24);

    // 2. Apply the DBC Scaling: Physical = (Raw * Factor) + Offset
    // Factor is 1, Offset is 0
    float physical_voltage = (static_cast<float>(raw_val) * 1.0f) + 0.0f;

    return physical_voltage;
}

int main() {
    // Example frame: Suppose the MPPT sends 0x00004A38 (19000 in decimal)
    // In Little Endian, this is stored as:
    uint8_t frame[8] = {0x38, 0x4A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    float voltage = extract_voltage(frame);
    std::cout << "Output Voltage: " << voltage << " V" << std::endl;

    return 0;
}