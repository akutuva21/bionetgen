import subprocess
import os

def test_print_error():
    process = subprocess.Popen(
        ['../bin/run_network'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd='bng2/Network3/src'
    )
    stdout, stderr = process.communicate()
    exit_code = process.returncode

    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    expected_output = """Usage:
run_network  [-bcdefkmsvx] [-a atol] [-g groupfile] [-h seed] [-i start_time] [-o outprefix] [-r rtol] [-t tol] [-z iteration number] netfile sample_time n_sample
or
run_network  [-bcdefkmsvx] [-a atol] [-g groupfile] [-h seed] [-i start_time] [-o outprefix] [-r rtol] [-t tol] [-z iteration number] netfile t1 t2 ... tn
"""
    assert expected_output == stderr.decode('utf-8'), "Stderr output did not match expected"
    print("test_print_error passed!")

if __name__ == '__main__':
    test_print_error()
