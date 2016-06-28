import unittest
import pprint
import sys
import os
import json

# The test object
from template import TemplateRex

fspec_template =  't-detail.html'
fspec_tsections =  "./test_data/tsections_base.py"
fspec_render =  "./test_data/trender_base.html"

fspec_data_flwr =  "./test_data/data_flwr.json"

# set as true to make new set to test data
tdata_make = False
if tdata_make: print("\nWarning test data be generated!\n\n")

class TestCase(unittest.TestCase):

  def test_template_base_process(self):

    trex = TemplateRex(fname=fspec_template)

    if tdata_make:
      fid = open( fspec_tsections  ,'w')
      pprint.pprint(trex.tsections,stream=fid)
      print("Creating ",fspec_tsections," test data")
      fid.close()

    fid = open( fspec_tsections,'r')
    tsections_str = fid.read()
    fid.close()

    #self.assertTrue(trex.tsections,tsections_str)


  def test_template_base_render(self):
    trex = TemplateRex(fname=fspec_template)

    fid = open(fspec_data_flwr,'r')
    row_data = json.load(fid)
    fid.close()

    inc = 1
    for row in row_data[0]:
      row['inc'] = inc
      trm = trex.render_sec('row', row )
      inc += 1

    rtn = trex.render_sec('tbl')
    rtn = trex.render_sec('ftr')
    rtn = trex.render_sec('content')
    rtn_str = trex.render()

    #print("--------------\n",rtn_str,"------------\n")

    if tdata_make:
      fid = open( fspec_render  ,'w')
      fid.write(rtn_str)
      fid.close()
      print("\nCreating!!!! ",fspec_render," test data")


    fid = open( fspec_render,'r')
    trender_str = fid.read()
    fid.close()

    self.assertTrue(rtn_str == trender_str)




if __name__ == '__main__':
    unittest.main()
