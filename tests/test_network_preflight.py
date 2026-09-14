"""Run the real shell preflight with mocked OS commands; never touches DNS."""
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'terraform/files/network-preflight.sh'


class NetworkPreflightTests(unittest.TestCase):
    def run_shell(self, scenario):
        script = '''
set -eu
source "$1"
timeout() { shift; "$@"; }
sleep() { :; }
install() { :; }
cp() { :; }
dnf() { echo DNF; }
''' + scenario
        return subprocess.run(['bash', '-c', script, 'preflight-test', str(SCRIPT)],
                              capture_output=True, text=True, timeout=5)

    def test_healthy_dns_does_not_reload(self):
        result = self.run_shell('''
getent() { return 0; }
nmcli() { echo UNEXPECTED_RELOAD; return 1; }
stand_install_packages
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('UNEXPECTED_RELOAD', result.stdout)
        self.assertEqual(result.stdout.count('DNF'), 1)

    def test_stale_dns_is_reloaded_before_packages(self):
        result = self.run_shell('''
ready=0
getent() { [[ "$ready" == 1 ]]; }
nmcli() { [[ "$*" == "general reload dns-rc" ]]; ready=1; echo RELOADED; }
stand_install_packages
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(result.stdout.index('RELOADED'), result.stdout.index('DNF'))

    def test_persistent_dns_failure_stops_before_packages(self):
        result = self.run_shell('''
getent() { return 1; }
nmcli() { echo RELOAD_ATTEMPT; return 1; }
stand_install_packages
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('DNF', result.stdout)
        self.assertEqual(result.stdout.count('RELOAD_ATTEMPT'), 6)
        self.assertIn('DNS não recuperado', result.stderr)

    def test_package_retry_is_bounded(self):
        result = self.run_shell('''
getent() { return 0; }
dnf() { echo DNF; return 1; }
stand_install_packages
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count('DNF'), 3)

    def test_cloud_init_does_not_install_before_preflight(self):
        root = SCRIPT.parent.parent
        cloud = (root / 'cloud-init.yaml.tftpl').read_text()
        bootstrap = (SCRIPT.parent / 'bootstrap.sh').read_text()
        self.assertNotIn('\npackages:', cloud)
        self.assertIn('package_update: false', cloud)
        self.assertLess(bootstrap.index('stand_install_packages'), bootstrap.index('curl --fail'))


if __name__ == '__main__':
    unittest.main()
