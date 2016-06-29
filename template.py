import os
import os.path
import re
from string import Template

import fnmatch
import pprint
import marshal

pp = pprint.PrettyPrinter(indent=4)

class TemplateRex:
    
    template_dirs = ["./", "./templates"]
    
    cmnt_prefix = '<!--'
    cmnt_postfix = '-->'
    func_prefix = '&'
        
       # ----------------------
    def __init__(self, **args):

        #if 'fname' in args.keys():
        #    self.fname = args['fname']
        #else: raise Exception('fname arguement required')

        self.cmnt_verbose = 1
        self.func_registered = {}

        self.tsections = {}                        # template sections
        self.psections = { 'main':"", 'base':""}   # processed sections
        self.csections = { 'main':[], 'base':[] }  # child sections
        self.last_parent = ['main']     # used to determine last found parent in recursive func

        self.block_pattern = self.cmnt_prefix + r'\s*BEGIN name=(?P<nm>\w+)\s*' + self.cmnt_postfix + r'(?P<inner>.*?)' + self.cmnt_prefix + r'\s*END name=\1 ' + self.cmnt_postfix
        self.base_pattern  = self.cmnt_prefix + r'\s*BASE name=(?P<nm>\S+)\s*' + self.cmnt_postfix
        self.func_pattern  = self.func_prefix + r'(?P<fn_nm>\S+)\((?P<fn_args>.*?)\)'

        self.block_re = re.compile(self.block_pattern, re.DOTALL)
        self.func_re  = re.compile(self.func_pattern)

        for key in args.keys():
            self.__dict__[key] = args[key]

        # load template based on a search list
        self.load_template(self.fname)
       
    # ----------------------
    def load_template(self,fname):
        """ Loads a template into self.tsection """

        for dir_spec in self.template_dirs:
            fspec = os.path.join(dir_spec, fname)
            if os.path.isfile(fspec):

                # Assumes ext .html but replace twice as fast as re
                fspec_msh = fspec.replace('.html','.msh')
                if os.path.isfile(fspec_msh):
                    if os.stat(fspec_msh).st_mtime > os.stat(fspec_msh).st_mtime:
                        fid = open(fspec_msh, 'rb')
                        self.tsections = marshal.load(fid)
                        fid.close()
                else:
                    fid = open(fspec, 'r')
                    file_str = fid.read()
                    fid.close()

                    # First check for a base specifier
                    match = re.match(self.base_pattern, file_str)
                    if match:
                        fname_base = match.group('nm')
                        # Save to 'base' as this is rendered in the final render if present
                        self.tsections['base'] = self.load_template(fname_base)
                        
                    self.tsections['main'] = self.process_template(file_str)
                    
                    # if compile_flg marshal tsections to fspec_msh

                break

        if not self.tsections:
            raise Exception('No Template File Found in -> ' +  ' , '.join(self.template_dirs) )

        return self.tsections['main']

    # ----------------------
    def process_template(self, t_str):

        def process_capture(obj):

            name_sec = obj.group(1)

            self.csections[name_sec] = []
            self.last_parent.append(name_sec)

            proc_rtn = self.process_template(obj.group(2))  # recursive call group(2) is next template section

            self.last_parent.pop()
            self.csections[self.last_parent[-1]].append(name_sec)

            self.tsections[name_sec] = proc_rtn.rstrip()
            self.psections[name_sec] = ""   # need to initialize to blank unrendered blocks
            return "$" + name_sec

        section = self.block_re.sub(process_capture, t_str, re.DOTALL)
        return section

    # ----------------------
    def render_sec(self, section, context={}):

        tmpl = Template(self.tsections[section])
        context.update(self.psections)

        self.psections[section] = tmpl.safe_substitute(context)

        # Clear the child process sections making avaible for next use
        for child in self.csections[section]:
            self.psections[child] = ""

        if self.func_registered:
            self.subtitute_functions(section)

        return(self.psections[section])

    # ----------------------
    def render(self, context={}):
        """ render the main section and if base was used render that instead """
        if "base" in self.tsections:
            rtn = self.render_sec("base", context)
        else:
            rtn = self.render_sec("main", context)
            
        for sec in self.psections:
            self.psections[sec] = ""
        return rtn

    # ----------------------
    def subtitute_functions(self, section):

        def process_capture(obj):
            
            rtn = ""
            func_name = obj.group(1)
            if func_name in self.func_registered:
                args = obj.group(2)
                if args:
                  arg_lst = args.split(',')
                  rtn = self.func_registered[func_name](*arg_lst)
                else:
                  rtn = self.func_registered[func_name]()

            return rtn

        self.psections[section] = self.func_re.sub(process_capture, self.psections[section], re.DOTALL)

