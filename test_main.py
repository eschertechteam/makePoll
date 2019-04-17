"""
Unit test plan for the make_poll package
sudo apt-get install python-nose python3-nose
run by `python3 -m "nose" test_main.py`
"""

from unittest.mock import patch, Mock
from nose.tools import eq_

from make_poll import next_available_row, getForm

class FakeWKS():

    def __init__(self, col_vals=None, row_vals=None):
        # python list is mutable. use None decide if we want an 
        # empty list as the default
        self.col_vals = col_vals if col_vals else []
        self.row_vals = row_vals if row_vals else []

    def col_values(self, col_in):
        return self.col_vals

    def row_values(self, row_in):
        return self.wks[0][0]

class TestMain():
    
    def test_next_available_row(self):
        # TODO: Patch wks, assert on available row is expected
        fake_wks_vals = [[], [1, 1, 1, None], [1], [None]]
        fake_wks_objs = [FakeWKS(col_vals=vals) for vals in fake_wks_vals]
        expected = ['1', '4', '2', '1']
        actual = [next_available_row(wks) for wks in fake_wks_objs]
        for i in range(len(expected)):
            eq_(expected[i], actual[i], 'Wrong next row index returned')

    def test_formatDate(self):
        pass

    def test_checkTime(self):
        pass

    @patch('uuid.uuid1')
    @patch('make_poll.getForm', return_value=FakeWKS())
    @patch('make_poll.next_available_row', return_value='10')
    def test_get_context(self, mock_row, mock_form, mock_uuid):
        # TODO: move generate context to its own function
        # Patch datetime, uuid, assert on config['context'] 

        """        
        mock_uuid.int.return_value = 99999
        actual_ctx = make_poll.gen_context
        expected_ctx = 'hard-coded'
        eq_(expected_ctx, actual_ctx, msg='Context generation does not match expected context')
        """
        pass