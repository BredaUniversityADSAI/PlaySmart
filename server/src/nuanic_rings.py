from dataclasses import dataclass
from typing import List
import time
import struct

service_uuid = '5491faaf-b0c2-4167-8f3d-bc6b31db69e7'
sample_rate_uuid = '516b0fb6-d861-4619-9dd0-0105e8b85128'
realtime_uuid = 'dc9c31a7-fbd3-467a-8777-10900c423d3b'
dne_uuid = 'd306262b-c8c9-4c4b-9050-3a41dea706e5'
eda_uuid = '42dcb71b-1817-43bd-8ea3-7272780a1c9f'
storage_uuid = '7c3b82e7-22b7-4cb6-8458-ba325edf6ede'
storage_format_uuid = '3cce21a7-e602-4e02-8c52-1e0366c1c846'
storage_usage_uuid = 'd78e5bd8-53d6-4fc3-bc98-03b8cd71684b'
command_uuid = '741f0d15-cc3d-4715-a9fb-a5a6bccebc50'
state_uuid = '3c180fcc-bfec-4b7c-8e52-1a37f123e449'

@dataclass
class EDA:
    boot_count: int
    timestamp: int  # Timestamp in seconds
    eda: int  # EDA value in Ohms

@dataclass
class DNE:
    boot_count: int
    timestamp: int  # Timestamp in seconds
    srrn: int  # Skin resistance reactions per minute
    srl: int   # Skin resistance level (tonic)
    dne: int   # DNE value

# Function to get current timestamp in seconds
def current_timestamp():
    return int(time.time())  # Current time in seconds

# Sample data creation
eda_data = EDA(
    boot_count=1,
    timestamp=current_timestamp(),
    eda=3500
)

dne_data = DNE(
    boot_count=1,
    timestamp=current_timestamp(),
    srrn=25,
    srl=1200,
    dne=75
)

print(f"EDA Data: {eda_data}")
print(f"DNE Data: {dne_data}")

def parse_eda(data):
    item_size = 2 + 8 + 4  # bootcount (2 bytes) + timestamp (8 bytes) + eda (4 bytes)
    item_count = len(data) // item_size
    eda_list = []

    for i in range(item_count):
        base = i * item_size
        bootcount = struct.unpack_from('<H', data, base)[0]
        timestamp = struct.unpack_from('<Q', data, base + 2)[0]
        eda = struct.unpack_from('<i', data, base + 2 + 8)[0]
        
        eda_list.append({
            'bootcount': bootcount,
            'timestamp': timestamp,
            'eda': eda
        })
    
    return eda_list

def parse_dne(data):
    item_size = 2 + 8 + 4 + 4 + 4  # bootcount (2 bytes) + timestamp (8 bytes) + srrn (4 bytes) + srl (4 bytes) + dne (4 bytes)
    item_count = len(data) // item_size
    dne_list = []

    for i in range(item_count):
        base = i * item_size
        bootcount = struct.unpack_from('<H', data, base)[0]
        timestamp = struct.unpack_from('<Q', data, base + 2)[0]
        srrn = struct.unpack_from('<i', data, base + 2 + 8)[0]
        srl = struct.unpack_from('<i', data, base + 2 + 8 + 4)[0]
        dne = struct.unpack_from('<i', data, base + 2 + 8 + 4 + 4)[0]

        dne_list.append({
            'bootcount': bootcount,
            'timestamp': timestamp,
            'srrn': srrn,
            'srl': srl,
            'dne': dne
        })
    
    return dne_list

def request_mtu(size):
    print(f"Requested MTU: {size}")

def read_storage_format():
    # This is a placeholder function. Replace with actual storage format reading logic.
    # Let's assume it returns either 1 (EDA format) or 2 (DNE format).
    return 1

def read_storage():
    # This is a placeholder function. Replace with actual logic to read data.
    # For the sake of this example, return an empty bytes object to simulate no data.
    return b''

def main():
    # Request a high MTU for better performance
    request_mtu(498)
    
    # Check the storage format before reading any data
    format_type = read_storage_format()
    
    while True:
        # Read the data
        data = read_storage()
        
        # Zero bytes read -> no more data available
        if len(data) == 0:
            break
        
        # Parse the data based on the format
        if format_type == 1:
            eda_data = parse_eda(data)
            print("EDA Data:", eda_data)
        elif format_type == 2:
            dne_data = parse_dne(data)
            print("DNE Data:", dne_data)

if __name__ == '__main__':
    main()
