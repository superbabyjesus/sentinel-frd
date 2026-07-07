"""
Sentinel-FRD — Concurrency Lab: Sequential vs. Multi-Threaded Polling
Document Class: Network Programmability & Performance Engineering
Target CCNP Focus: ENCOR Section 6.0 (Automation & Network Programmability)

This lab script demonstrates the mathematical execution delta of polling multiple
Cisco nodes sequentially versus concurrently via ThreadPoolExecutor.

Formulas Verified:
  T_sequential = sum(t_i) 
  T_parallel   ≈ ceil(N / W) * max(latency) 
  (Where N = Nodes, W = Workers)
"""

import time
import concurrent.futures
from netmiko import ConnectHandler

# ==========================================
# LAB CONFIGURATION (GNS3 / Physical Nodes)
# ==========================================
# Populate this list with your local Sabaneta lab IP addresses.
# For testing without active hardware, we simulate connection delays.
LAB_NODES = [
    {
        'device_type': 'cisco_ios',
        'host': '192.168.100.1', # Core-R1
        'username': 'andres_admin',
        'password': 'YourSecurePassword',
        'secret': 'YourEnableSecret',
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.100.2', # Dist-SW1
        'username': 'andres_admin',
        'password': 'YourSecurePassword',
        'secret': 'YourEnableSecret',
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.100.3', # Access-SW1
        'username': 'andres_admin',
        'password': 'YourSecurePassword',
        'secret': 'YourEnableSecret',
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.100.4', # Access-SW2
        'username': 'andres_admin',
        'password': 'YourSecurePassword',
        'secret': 'YourEnableSecret',
    }
]

SIMULATE_HARDWARE = True # Set to False when connecting to live GNS3 nodes

def poll_node(node_params):
    """
    Simulates or executes an SSH command audit over a single Cisco Node.
    """
    host = node_params['host']
    start_time = time.time()
    
    if SIMULATE_HARDWARE:
        # Simulate network latency and Cisco CLI command execution delays
        # SSH Handshake (~1.5s) + Enable Mode (~0.5s) + Command execution (~1s)
        time.sleep(3.0) 
        execution_time = time.time() - start_time
        return {
            "host": host,
            "status": "SUCCESS (SIMULATED)",
            "output": "OSPF Process 1 Neighbor ID: 10.0.0.2 State: FULL",
            "execution_time": round(execution_time, 2)
        }
        
    try:
        # Live Netmiko execution path
        connection = ConnectHandler(**node_params)
        connection.enable()
        output = connection.send_command("show ip ospf neighbor")
        connection.disconnect()
        
        execution_time = time.time() - start_time
        return {
            "host": host,
            "status": "SUCCESS",
            "output": output,
            "execution_time": round(execution_time, 2)
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "host": host,
            "status": "FAILED",
            "error": str(e),
            "execution_time": round(execution_time, 2)
        }

# ==========================================
# EXECUTION PATHS
# ==========================================

def run_sequential_audit(nodes):
    """Executes audits one by one. Expected complexity: O(N)"""
    print("\n[*] Starting Sequential Diagnostic Scan...")
    start_time = time.time()
    results = []
    
    for node in nodes:
        print(f"  -> Polling {node['host']}...")
        result = poll_node(node)
        results.append(result)
        
    total_duration = time.time() - start_time
    return results, total_duration

def run_concurrent_audit(nodes, max_workers=10):
    """Executes audits concurrently via a Thread Pool. Expected complexity: O(1)"""
    print("\n[*] Starting Concurrent Diagnostic Scan...")
    start_time = time.time()
    
    # We use ThreadPoolExecutor because network automation is heavily I/O-bound.
    # The Python GIL (Global Interpreter Lock) is released during socket waits.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map submits the poll_node function across the list of nodes
        results = list(executor.map(poll_node, nodes))
        
    total_duration = time.time() - start_time
    return results, total_duration

# ==========================================
# PERFORMANCE ANALYSIS & COMPILATION
# ==========================================

if __name__ == "__main__":
    print("="*60)
    print("    CCNP NetDevOps Lab: Concurrency & Performance Engine")
    print("="*60)
    print(f"Targeting: {len(LAB_NODES)} Network Nodes")
    print(f"Simulation Mode: {SIMULATE_HARDWARE}")
    
    # 1. Run Sequential
    seq_results, seq_time = run_sequential_audit(LAB_NODES)
    print(f"[+] Sequential Scan Completed in: {seq_time:.2f} seconds.")
    
    # 2. Run Concurrent
    con_results, con_time = run_concurrent_audit(LAB_NODES, max_workers=4)
    print(f"[+] Concurrent Scan Completed in: {con_time:.2f} seconds.")
    
    # 3. Report the Math Delta
    performance_increase = (seq_time / con_time)
    print("\n" + "="*40)
    print("        PERFORMANCE REPORT")
    print("="*40)
    print(f"Sequential Execution (T_seq): {seq_time:.2f}s")
    print(f"Concurrent Execution (T_par): {con_time:.2f}s")
    print(f"NetDevOps Performance Delta:  {performance_increase:.1f}x FASTER!")
    print("="*40)
    
    print("\nCCNP ENCOR Key Takeaway:")
    print("  Although Python uses a Global Interpreter Lock (GIL), multi-threading is")
    print("  highly effective for network automation because the GIL is released")
    print("  while threads wait for network socket connections (I/O blocks).")
    print("="*60)