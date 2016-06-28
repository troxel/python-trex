import unittest
import pprint
import sys
import json

# The test object
from template import TemplateRex

fspec_template =  't-home.html'
fspec_tsections =  "./test_data/tsections.py"
fspec_render =  "./test_data/trender.html"

fspec_data_cell =  "./test_data/data_cell.json"
fspec_data_flwr =  "./test_data/data_flwr.json"

# set as true to make new set to test data
tdata_make = False
if tdata_make: print("Warning test data be generated!")

class TestCase(unittest.TestCase):

  def test_template_process(self):

    trex = TemplateRex(fname=fspec_template)

    if tdata_make:
      fid = open( fspec_tsections  ,'w')
      pprint.pprint(trex.tsections,stream=fid)
      print("Creating ",fspec_tsections," test data")
      fid.close()

    fid = open( fspec_tsections,'r')
    tsections_str = fid.read()
    fid.close()
    self.assertTrue(trex.tsections,tsections_str)

  def test_template_render(self):
    trex = TemplateRex(fname=fspec_template)

    fid = open(fspec_data_flwr,'r')
    row_data = json.load(fid)
    fid.close()

    for row in row_data[0]:
      trm = trex.render_sec('row', row )
    rtn = trex.render_sec('tbl',{'category':'Flowers'})

    for row in row_data[1]:
      trm = trex.render_sec('row', row )
    rtn = trex.render_sec('tbl',{'category':'Fruit'})

    # Complex table with each cell rendered
    fid = open(fspec_data_cell,'r')
    cell_data = json.load(fid)
    fid.close()

    inx=0
    for cell in cell_data:
      trm = trex.render_sec('cell_complex', cell)
      inx += 1
      if not inx%4:
        trex.render_sec('row_complex')

    trex.render_sec('row_complex')
    trex.render_sec('tbl_complex')

    rtn = trex.render_sec('ftr')
    rtn_str = trex.render()

    ##print(rtn_str)

    if tdata_make:
      fid = open( fspec_render  ,'w')
      fid.write(rtn_str)
      fid.close()
      print("Creating ",fspec_render," test data")

    fid = open( fspec_render,'r')
    trender_str = fid.read()
    fid.close()

    self.assertTrue(rtn_str == trender_str)


if __name__ == '__main__':
    unittest.main()
