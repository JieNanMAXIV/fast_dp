from __future__ import absolute_import, division, print_function

import os
import procrunner
import pytest

def test_fast_dp_X4_wide(tmpdir):
  X4_wide = '/dls/science/groups/scisoft/DIALS/regression_data/X4_wide'
  if not os.path.exists(X4_wide):
    pytest.skip('Could not find test image file')

  image = os.path.join(X4_wide, 'X4_wide_M1S4_2_0001.cbf')

  bin = os.path.split(__file__)[0].replace('src', 'bin')
  fast_dp = os.path.join(bin, 'fast_dp')

  cmd = [ fast_dp, '-a', 'Ba', image ]
  with tmpdir.as_cwd():
    result = procrunner.run(cmd)

  assert result['stderr'] == '', 'fast_dp output to STDERR:'
  assert result['exitcode'] == 0, 'fast_dp non-zero exit code'
  for output in ['fast_dp.mtz', 'fast_dp.log']:
    assert tmpdir.join(output).check(), 'No output found'