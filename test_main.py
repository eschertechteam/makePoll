"""
Unit test plan for the make_poll package
run by `nosetests test_main.py`
"""

from mock import patch, Mock
from nose.tools import eq_

# from make_poll.__main__ import next_available_row, getForm

class FakeWKS():

    def __init__():
        # self.wks = pd.Dataframe([1, 2, 3])

    def col_values(col_in):
        return [1, 2, 3, None]

    def row_values(row_in):
        return self.wks[0][0]

class TestMain():
    
    
    def test_next_available_row(self):
        # TODO: Patch wks, assert on available row is expected
        pass

    @mock.patch('ServiceAccountCredentials.from_json_keyfile_name')
    @mock.patch('gspread.authorize')
    def test_get_form(self, mock_gc, mock_creds):
        # TODO: Patch service accnt load creds, gspread authorize, assert sheet
        expected = 'form_name_str'
        mock_gc.open.assert_called_once_with(expected)
        pass

    @mock.patch('uuid.uuid1')
    @mock.patch('datetime.strptime')
    @mock.patch('make_poll.getForm', return_value=FakeWKS())
    @mock.patch('make_poll.next_available_row', return_value='10')
    def test_get_context(self, mock_row, mock_form, mock_datetime, mock_uuid):
        # TODO: move generate context to its own function
        # Patch datetime, uuid, assert on config['context'] 

        mock_uuid.int.return_value = 99999
        actual_ctx = make_poll.gen_context
        expected_ctx = 'hard-coded'
        eq_(expected_ctx, actual_ctx, msg='Context generation does not match expected context')
        pass
