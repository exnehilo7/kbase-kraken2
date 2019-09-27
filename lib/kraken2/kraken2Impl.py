# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pandas as pd

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
#END_HEADER


class kraken2:
    '''
    Module Name:
    kraken2

    Module Description:
    A KBase module: kraken2
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    def package_folder(self, folder_path, zip_file_name, zip_file_description):
        ''' Simple utility for packaging a folder and saving to shock '''
        if folder_path == self.shared_folder:
            raise ValueError ("cannot package scatch itself.  folder path: "+folder_path)
        elif not folder_path.startswith(self.shared_folder):
            raise ValueError ("cannot package folder that is not a subfolder of scratch.  folder path: "+folder_path)
        dfu = DataFileUtil(self.callback_url)
        if not os.path.exists(folder_path):
            raise ValueError ("cannot package folder that doesn't exist: "+folder_path)
        output = dfu.file_to_shock({'file_path': folder_path,
                                    'make_handle': 0,
                                    'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'label': zip_file_description}
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kraken2(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kraken2

        # Download input data as FASTA
        for name in ['input_genomes',
                     'workspace_name', 'db_type']:
            if name not in params:
                raise ValueError(
                    'Parameter "' + name + '" is required but missing')
        if not isinstance(params['input_genomes'], str) or not len(
                params['input_genomes']):
            raise ValueError('Pass in a valid input genome string')
        logging.info(params['input_genomes'], params['db_type'])

        assembly_util = AssemblyUtil(self.callback_url)
        fasta_file_obj = assembly_util.get_assembly_as_fasta(
            {'ref': params['input_genomes']})
        logging.info(fasta_file_obj)
        fasta_file = fasta_file_obj['path']

        output_dir = os.path.join(self.shared_folder, 'kraken2_output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


        # cmd = ['/kb/module/lib/kraken2/src/kraken2.sh', '--report',
        #        f'{fasta_file}.txt',
        #        '--db', '/data/kraken2/' + params['db_type'], '--threads', '1',
        #        '--input', fasta_file]
        report_file_name = 'report.txt'
        cmd = ['kraken2', '-db', '/data/kraken2/' + params['db_type'], '--report', report_file_name, '--threads', '1', fasta_file]
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')

        cmd0 = ["ls", '/kb/module/']
        logging.info(f'cmd {cmd0}')
        pls = subprocess.Popen(cmd0, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')

        cmd1 = ["ls", '/kb/module/test/']
        logging.info(f'cmd {cmd1}')
        pls = subprocess.Popen(cmd1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')

        cmd1 = ["ls", self.shared_folder]
        logging.info(f'cmd {cmd1}')
        pls = subprocess.Popen(cmd1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')
        # generate report directory and html file
        columns = [
            'Percentage of fragments covered by the clade rooted at this taxon',
            'Number of fragments covered by the clade rooted at this taxon',
            'Number of fragments assigned directly to this taxon', 'rank code',
            'taxid', 'name']
        report_file = os.path.join('/kb/module/test', report_file_name)
        report_df = pd.read_csv(report_file, sep='\t',
                                header=None, names=columns)
        report_html_file = os.path.join(output_dir, 'report.html')
        report_df.to_html(report_html_file, classes='Kraken2_report', index=False)
        html_zipped = self.package_folder(output_dir, 'report.html',
                                          'report')
        # Step 5 - Build a Report and return
        objects_created = []
        output_files = os.listdir(output_dir)
        output_files_list = []
        for output in output_files:
            if not os.path.isdir(output):
                output_files_list.append(
                    {'path': os.path.join(output_dir, output), 'name': output})
        message = f"Kraken2 run finished on {fasta_file} against {params['db_type']}."
        report_params = {'message': message,
                         'workspace_name': params.get('workspace_name'),
                         'objects_created': objects_created,
                         'file_links': output_files_list,
                         'html_links': [html_zipped],
                         'direct_html_link_index': 0,
                         'html_window_height': 460}

        # STEP 6: construct the output to send back
        kbase_report_client = KBaseReport(self.callback_url)
        report_output = kbase_report_client.create_extended_report(
            report_params)
        report_output['report_params'] = report_params
        logging.info(report_output)
        # Return references which will allow inline display of
        # the report in the Narrative
        output = {'report_name': report_output['name'],
                  'report_ref': report_output['ref']}
        #END run_kraken2

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kraken2 return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
